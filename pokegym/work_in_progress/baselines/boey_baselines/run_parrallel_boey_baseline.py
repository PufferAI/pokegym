'''
Baselines v3
Changes:
reduced vector_output_dim to 16 to see if it is the issue with vector observation

'''
from os.path import exists
from pathlib import Path
import uuid
from baselines.boey_baselines.red_gym_env import RedGymEnvV3 as RedGymEnv
from stable_baselines3 import PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from baselines.boey_baselines.custom_network import CustomCombinedExtractorV2
from baselines.boey_baselines.tensorboard_callback import TensorboardCallback

def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        env = RedGymEnv(env_conf)
        env.reset(seed=(seed + rank))
        return env
    set_random_seed(seed)
    return _init

def create_callbacks(use_wandb_logging=False):
    checkpoint_callback = CheckpointCallback(save_freq=ep_length, save_path=sess_path,
                                     name_prefix='poke')
    
    callbacks = [checkpoint_callback, TensorboardCallback()]

    if use_wandb_logging:
        import wandb
        from wandb.integration.sb3 import WandbCallback
        # wandb.tensorboard.patch(root_logdir=str(sess_path / Path('PPO_1')))
        run = wandb.init(
            project="pokemon-train",
            id=sess_id,
            config=env_config,
            sync_tensorboard=True,  
            monitor_gym=True,  
            save_code=True,
        )
        callbacks.append(WandbCallback())
    else:
        run = None
    return callbacks, run

if __name__ == '__main__':

    use_wandb_logging = False
    cpu_multiplier = 1.0  # 1.0 = 32 num_cpu, this is to scale and maintain the same number of training steps per training iteration
    ep_length = 2048 * 10 * 4  # increased ep length for converging model, added early stop
    n_steps = int(5120 // cpu_multiplier)  # to maintain ~163_840 steps per training iteration
    sess_id = str(uuid.uuid4())[:8]
    sess_path = Path(f'session_{sess_id}_env8_lr3e-4_ent01_bs512_5120_81920_0.5vf')
    num_cpu = int(32 * cpu_multiplier)  # Also sets the number of episodes per training iteration
    env_config = {
                'headless': True, 'save_final_state': True, 'early_stop': True,
                'action_freq': 24, 'init_state': 'has_pokedex_nballs.state', 'max_steps': ep_length, 
                'print_rewards': True, 'save_video': False, 'fast_video': True, 'session_path': sess_path,
                'gb_path': 'PokemonRed.gb', 'debug': False, 'sim_frame_dist': 2_000_000.0, 
                'use_screen_explore': False, 'reward_scale': 4, 
                'extra_buttons': True, 'restricted_start_menu': True,
                'randomize_first_ep_split_cnt': num_cpu,
                # 'start_from_state_dir': state_dir, 'save_state_dir': state_dir,
                'explore_weight': 1.5, # 3
            }
    
    print(env_config)
    
    env = SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])
    

    # env = make_env(0, env_config)
    # env_checker.check_env(RedGymEnv(env_config))
    learn_steps = 40
    # put a checkpoint here you want to start from
    file_name = ''
    if file_name and not exists(file_name + '.zip'):
        raise Exception(f'File {file_name} does not exist!')
    if exists(file_name + '.zip'):
        print('\nloading checkpoint')
        model = PPO.load(file_name, env=env)
        model.n_steps = n_steps
        model.n_envs = num_cpu
        model.rollout_buffer.buffer_size = n_steps
        model.rollout_buffer.n_envs = num_cpu
        model.rollout_buffer.reset()
        print(model.policy)
        print(f'Loaded model --- LR: {model.learning_rate} OptimizerLR: {model.policy.optimizer.param_groups[0]["lr"]}, ent_coef: {model.ent_coef}')
    
    else:
        print('\ncreating new model with [512, 512] fully shared layer')
        import torch
        policy_kwargs = dict(
            features_extractor_class=CustomCombinedExtractorV2,
            share_features_extractor=True,
            net_arch=[512, 512],  # dict(pi=[256, 256], vf=[256, 256])
            activation_fn=torch.nn.ReLU,
        )
        model = PPO('MultiInputPolicy', env, verbose=1, n_steps=n_steps, batch_size=512, n_epochs=10, gamma=0.998, tensorboard_log=sess_path,
                    ent_coef=0.01, learning_rate=0.0003, vf_coef=0.5,
                    policy_kwargs=policy_kwargs)
        
        print(model.policy)

        print(f'start training --- LR: {model.learning_rate} OptimizerLR: {model.policy.optimizer.param_groups[0]["lr"]}, ent_coef: {model.ent_coef}')
    
    callbacks, run = create_callbacks(use_wandb_logging)
    
    for i in range(learn_steps):
        model.learn(total_timesteps=(ep_length)*num_cpu*1000, callback=CallbackList(callbacks))

        
    if run:
        run.finish()