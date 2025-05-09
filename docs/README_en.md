# Deep Code

## Setup
1. Create a conda environment
```bash
conda create -n deep_code python=3.12
pip activate deep_code
```

2. Install torch with matching GPU or CPU.

For example,
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

3. Install dependencies
```bash
pip install -r requirements
```