#!/bin/sh

# Clone optimum-habana
# if [ ! -d "$(pwd)/optimum-habana" ]; then
#     git clone https://github.com/huggingface/optimum-habana.git $(pwd)/optimum-habana
# fi

# Option 1: Use the latest stable release
pip install --upgrade-strategy eager optimum[habana]
# Option 2: Use the latest main branch under development
pip install git+https://github.com/huggingface/optimum-habana.git
# To use DeepSpeed on HPUs, you also need to run the following command:
pip install git+https://github.com/HabanaAI/DeepSpeed.git@1.15.0

# install requirements from each examples
