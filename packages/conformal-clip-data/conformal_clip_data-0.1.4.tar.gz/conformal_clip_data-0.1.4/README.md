# conformal-clip-data

A companion data package providing benchmark datasets for the [**clip-conformal**](https://github.com/fmegahed/clip-conformal) package.

## Overview

This package bundles the simulated textile image dataset used in **[Megahed et al., 2025](https://arxiv.org/pdf/2501.12596)** for demonstrating conformal prediction with CLIP-based few-shot image classification in manufacturing quality control applications.

**This is a data-only package** designed to work seamlessly with the **clip-conformal** package (coming soon to PyPI), which provides the core implementation of conformal prediction methods for CLIP models. By separating data from implementation, we keep the main package lightweight while providing easy access to reproducible benchmark datasets.

## Installation

Install from PyPI (data only):

```bash
pip install conformal-clip-data
```

Optional image preview tools (Pillow + matplotlib) as an extra:

```bash
pip install "conformal-clip-data[standalone]"
```

Install from source:

```bash
git clone https://github.com/fmegahed/conformal-clip-data.git
cd conformal-clip-data
pip install -e .
# with preview tools: pip install -e .[standalone]
```

## Quick Start

```python
from conformal_clip_data import textile_simulated_root, nominal_dir, local_dir, global_dir

# Access the textile dataset root
textile_path = textile_simulated_root()
print(f"Textile dataset location: {textile_path}")

# Access specific image categories
print(f"Nominal images: {nominal_dir()}")
print(f"Local defect images: {local_dir()}")
print(f"Global defect images: {global_dir()}")
```

### Quick Image Peek (optional)

If you installed the optional extras (`[standalone]`), you can quickly visualize a few samples:

```python
from conformal_clip_data import nominal_dir, local_dir, global_dir
import random
from PIL import Image
import matplotlib.pyplot as plt

samples = []
for d in [nominal_dir(), local_dir(), global_dir()]:
    files = list(d.glob("*.jpg"))
    samples += random.sample(files, k=min(3, len(files)))

cols = 3
rows = (len(samples) + cols - 1) // cols
plt.figure(figsize=(12, 4 * rows))
for i, f in enumerate(samples, 1):
    plt.subplot(rows, cols, i)
    plt.imshow(Image.open(f), cmap="gray")
    plt.title(f.parent.name + " / " + f.name)
    plt.axis("off")
plt.tight_layout()
plt.show()
```

### Verify Installation

Note on names (PEP 503 normalization):

- We publish as `conformal-clip-data`; pip also accepts `conformal_clip_data` and resolves to the same project.

Quick check in your shell:

```bash
python -c "import conformal_clip_data as c, sys; print(c.__version__); print(c.__file__); print(sys.executable)"
```

Colab tip: use `%pip install conformal-clip-data` in one cell, then import in a new cell.

## Dataset Provenance

These images were originally generated using the R script below and were previously released under an MIT License in our repository:

-   Image generation script: https://raw.githubusercontent.com/fmegahed/qe_genai/refs/heads/main/data/textile_images/extract_textile_images_from_r_textile_pkg.R

-   Original dataset release: https://github.com/fmegahed/qe_genai/tree/main/data/textile_images

### Dataset Summary

To systematically evaluate CLIP's performance on STS image
classification, we used the **spc4sts** R package to create a controlled
dataset of simulated textile fabric textures. This approach allowed us
to precisely model both nominal and defective weave structures and to
control defect type and severity.

Our dataset contains:

| Class | Description | Count |
|-------|-------------|-------|
| Nominal | Standard textile weave patterns | 1,000 |
| Local defects | Localized disruptions in the weave | 500 |
| Global defects | Systematic shifts in weave parameters | 500 |

Each image is **250 × 250 px**, generated using `spc4sts` recommended
parameters:

-   **Nominal images:**\
    Spatial autoregressive parameters ϕ₁ = 0.6, ϕ₂ = 0.35

-   **Global defects:**\
    Both parameters reduced by **5%**

-   **Local defects:**\
    Generated using the package's defect-insertion functions

## Relationship with clip-conformal

This data package is designed as a **companion to the clip-conformal package**, which will be released to PyPI shortly. The separation of concerns provides several benefits:

- **Lightweight installation**: The clip-conformal package remains small and fast to install
- **Reproducibility**: Benchmark datasets are versioned and distributed consistently
- **Extensibility**: Additional datasets can be added without modifying the core package
- **Optional usage**: Users can work with clip-conformal using their own data without downloading benchmark datasets

For the full implementation of conformal prediction methods for CLIP models and complete examples using this dataset, please install the **clip-conformal** package (coming soon).

## Citation

If you use this dataset in your research, please cite:

```bibtex
@misc{megahed2025adaptingopenaisclipmodel,
      title={Adapting OpenAI's CLIP Model for Few-Shot Image Inspection in Manufacturing Quality Control: An Expository Case Study with Multiple Application Examples},
      author={Fadel M. Megahed and Ying-Ju Chen and Bianca Maria Colosimo and Marco Luigi Giuseppe Grasso and L. Allison Jones-Farmer and Sven Knoth and Hongyue Sun and Inez Zwetsloot},
      year={2025},
      eprint={2501.12596},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2501.12596},
}
```

And the original spc4sts package used to generate the textile images:

```bibtex
@article{bui2020spc4sts,
  title={spc4sts: Statistical process control for stochastic textured surfaces in R},
  author={Bui, Anh Tuan and Apley, Daniel W},
  journal={Journal of Quality Technology},
  volume={53},
  number={3},
  pages={219--242},
  year={2020},
  doi={10.1080/00224065.2019.1707730}
}
```

## License

MIT License. These images were generated by the authors and are released under the MIT License. See [LICENSE](LICENSE) for details.
