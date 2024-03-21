# PokeGym Project Overview
# original project author: https://github.com/PWhiddy/PokemonRedExperiments
# join the Discord: http://discord.gg/RvadteZk4G

## This repo should be used for Pokemon Red RL development.
## Pokegym is a heavily-modified, heavily-improved version of the original code. Ultimately, the goal is to beat Pokemon Red using as pure RL as possible.

- **Best Run Yet**: Gets Badge 3 (Lt. Surge)
- **Achievements**:
  - Most environments secure **Badges 1 and 2**.
  - Badge 1 achieved at **9.6 million steps**.
  - Badge 2 achieved at **35 million steps**.
  - **Bill saved** at 53 million steps.
  - **86% of environments obtained HM01 (Cut)** with the first HM01 obtained at 60 million steps.
  - **68% of environments taught Cut** to a Pokémon.
  - Some environments reached **Celadon City** and entered Gym 3 using Cut.
  - **Puzzle completed**.
  - Badge 3 achieved at 404 million steps.
- **WandB Search Regex**: `badge_1|badge_2|badge_3|bill_saved|cut_taught|hm|cut_coord|map|lev|self.badg|deat`
- **WandB Overview**: [View Run Overview](https://wandb.ai/xinpw8/pufferlib/runs/2ffnd4xg/overview?nw=nwuserxinpw8)

## To install (advanced users):
PufferLib Guide
Use Linux or WSL if you are on Windows. It does work on mac with some tweaks.

Installation
First, star PufferLib, Pokemon Red, and Pokegym on Github (hey, gotta promote, right?). Then:

git clone -b 0.5 https://github.com/pufferai/pufferlib && cd pufferlib
pip install -e ".[cleanrl,pokemon_red]"
cp pokemon_red.gb pufferlib/
cp kanto_map_dsv.png pufferlib/

Run training. You will need to make a wandb account.
python demo.py --train --vectorization multiprocessing --track --wandb-entity YOUR_WANDB_USERNAME

Watch a pretrained model play
python demo.py --env pokemon_red_pip --evaluate PATH_TO_YOUR_MODEL

Play the game
pokegym.play

You can use custom models with --evaluate PATH. They must be compatible (i.e. trained for this version of the env)


## To install (complete amateurs):
 just installed today (WSL2 on Win10) using VS Code. The following is how I did it, provided for the aspiring dilettantes.

In VS Code I have the following pertinent Extensions installed locally: Dev Containers, Docker, and WSL. 

To get started, I went to github and Starred PufferLib, PufferTank, and PokemonRedExperiments. Then, I followed the instructions at the following address first for getting the puffertank Docker container working: https://github.com/PufferAI/PufferTank. I already had Docker Desktop and the Nvidia Container Toolkit installed, so I started at step 2.
In VS Code connected to WSL2: 

git clone https://github.com/PufferAI/PufferTank.git 

Naturally, Docker Desktop was running (in Win10). After the Docker container successfully loaded and was running in Docker Desktop, in VS Code, using the Search bar, I navigated to the PufferTank directory and selected "Open folder in dev container." Then I installed the VS Code Docker extension (in the Dev Container container). I then navigated to /workspaces/ as root and proceeded to follow these commands:

git clone -b pokemon_red https://github.com/pufferai/pufferlib && cd pufferlib
git checkout --track origin/pokemon_red
pip install -e '.[cleanrl,pokemon_red]'
cp pokemon_red.gb pufferlib/environments/

In retrospect I should have just followed the commands above instead of cloning the PufferTank repository first but it wasn't too much trouble (initially used the PufferTank config.py file, which had some conflicting packages; made sure to pip install -e '.[cleanrl,pokemon_red]' from /workspaces/pufferlib vs from /workspaces/PufferTank/puffertank/pufferlib). The final step cp pokemon_red.gb pufferlib/environments/ was done using a rom file outside of the PufferTank container. I then nagivated to cd ~ and installed FFmpeg:

apt install ffmpeg

That's it. 

cd /workspaces/pufferlib/ 

To run:
python demo.py --backend clean_pufferl --config pokemon_red --no-render --vectorization multiprocessing --mode train --track --wandb-entity xinpw8


## Configuration Summary

### Training Configuration (config.yaml provided in repo - place in PufferLib top dir)

- **Seed**: 1
- **Device**: CUDA
- **Learning Rate**: 0.00015
- **Gamma**: 0.998
- **GAE Lambda**: 0.95
- **Num Minibatches**: 4
- **Clip Coef**: 0.1
- **Ent Coef**: 0.01
- **VF Coef**: 0.5
- **Max Grad Norm**: 0.5
- **Verbose**: True
- **Data Dir**: `experiments`
- **Checkpoint Interval**: 200
- **CPU Offload**: True
- **BPTT Horizon**: 16
- **VF Clip Coef**: 0.1
- **Compile**: True
- **Compile Mode**: `reduce-overhead`

### Sweep Configuration

- **Method**: Random
- **Metric Goal**: Maximize episodic return
- **Parameters**:
  - **Learning Rate**: Log uniform values between 1e-4 and 1e-1
  - **Batch Size**: [128, 256, 512, 1024, 2048]
  - **Batch Rows**: [16, 32, 64, 128, 256]
  - **BPTT Horizon**: [4, 8, 16, 32]

### Environment Configuration

- **Total Timesteps**: 500,000,000
- **Number of Environments**: 72
- **Environments per Worker**: 1
- **Environments per Batch**: 24
- **Update Epochs**: 3
- **Batch Size**: 49152
- **Batch Rows**: 128
- **Gamma**: 0.998

## Milestone Timings

- **Badges 1 & 2**: Achieved efficiently with milestones at 9.6M and 35M steps respectively.
- **Bill Saved**: At 53M steps, indicating progress towards mid-game objectives.
- **HM01 (Cut)**: Obtained in 86% of environments, with the first HM01 at 60M steps.
- **Cut Taught**: In 68% of environments, demonstrating successful HM usage.
- **Advanced Progress**: Reaching Celadon City and Gym 3 highlights advanced navigation and puzzle-solving skills.
- **Badge 3**: Achieved at 404M steps, showcasing long-term training effectiveness.
