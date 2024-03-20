Run Params in Pufferlib:

pokemon_red:
  package: pokemon_red
  train:
    total_timesteps: 500_000_000
    num_envs: 96
    envs_per_worker: 1
    envs_per_batch: 32
    update_epochs: 3
    gamma: 0.998
    batch_size: 65536
    batch_rows: 128
    compile: True
    learning_rate: 2.0e-4
    anneal_lr: False
