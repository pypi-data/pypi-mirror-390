# Automating Leapfrog Workflows with Pollywog – An Independent Open-Source Tool

[![DOI-badge]][DOI] [![docs-badge]][docs] [![lite-badge]][lite]

[DOI-badge]: https://zenodo.org/badge/1071742254.svg
[DOI]: https://doi.org/10.5281/zenodo.173138
[docs-badge]: https://readthedocs.org/projects/pollywog/badge/?version=latest
[docs]: https://pollywog.readthedocs.io/en/latest/?
[lite-badge]: https://jupyterlite.rtfd.io/en/latest/_static/badge.svg
[lite]: https://endarthur.github.io/pollyweb

> **Pollywog** is a Python library for building, manipulating, and automating Leapfrog calculation sets programmatically.


## Table of Contents

- [Why Pollywog?](#why-pollywog)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Documentation](#documentation)
- [Contributing](#contributions)
- [License](#license)

## Why Pollywog?

If you work with [Leapfrog](https://www.seequent.com/products-solutions/leapfrog-geo/) for geological modeling and resource estimation, you know that building calculation sets (`.lfcalc` files) manually can be:

- **Time-consuming** – Repetitive point-and-click operations
- **Error-prone** – Easy to make mistakes in complex formulas
- **Hard to maintain** – Difficult to update across multiple projects
- **Not version-controlled** – Changes are hard to track and review
- **Not automatable** – Can't script or integrate with other tools

**Pollywog solves these problems** by letting you define calculations in Python code that is:

- Programmatic and automatable
- Version-controlled (Git-friendly)
- Testable and reproducible
- Easy to refactor and maintain
- Integrated with ML pipelines (scikit-learn)

## Key Features

### Core Functionality
- **Read and write** `.lfcalc` files programmatically
- **Create calculations** with Python classes (`Number`, `Category`, `If`, etc.)
- **Query and filter** calculation sets like pandas DataFrames
- **Topological sorting** for automatic dependency resolution
- **Rich display** in Jupyter notebooks with interactive trees

### Helper Functions
- **Mathematical operations**: `Sum`, `Product`, `Average`, `WeightedAverage`
- **Transformations**: `Scale`, `Normalize`
- **Classification**: `CategoryFromThresholds`
- **Dual mode**: Return complete calculations (with `name`) or expressions (without `name`) for composition

### Machine Learning Integration
- Convert **scikit-learn decision trees** to Leapfrog calculations
- Convert **random forests** to ensemble calculations
- Convert **linear models** to equations
- Support for both **regression and classification**

### Domain-Based Calculations
- Multi-domain resource modeling
- Weighted averages by domain proportions
- Conditional logic for different geological units

## Quick Start

```python
from pollywog.core import CalcSet, Number
from pollywog.helpers import WeightedAverage

# Create a calculation set
calcset = CalcSet([
    # Clean data
    Number("Au_clean", "clamp([Au], 0)",
           comment_equation="Remove negative values"),
    
    # Domain-weighted grade
    WeightedAverage(
        variables=["Au_oxide", "Au_sulfide", "Au_transition"],
        weights=["prop_oxide", "prop_sulfide", "prop_transition"],
        name="Au_composite",
        comment="Domain-weighted gold grade"
    ),
    
    # Apply recovery
    Number("Au_recovered", "[Au_composite] * 0.88",
           comment_equation="88% metallurgical recovery"),
])

# Export to Leapfrog
calcset.to_lfcalc("my_calculations.lfcalc")
```

Then import `my_calculations.lfcalc` into Leapfrog and you're done! ✨

> ⚠️ **Note**: Pollywog is in active development. Always backup your Leapfrog projects before testing. Report issues on [GitHub](https://github.com/endarthur/pollywog/issues).

## Legal Disclaimer

Pollywog is an independent open-source tool developed to support the automation of workflows involving .lfcalc files used in Leapfrog software by Seequent.
This tool does not perform reverse engineering, does not modify Leapfrog, and does not access its source code or proprietary libraries. Pollywog operates exclusively on user-generated files and is designed to complement Leapfrog through external automation.

Important:
- Pollywog is not affiliated with, endorsed by, or sponsored by Seequent or any company associated with Leapfrog
- Use of this tool does not violate Leapfrog’s license terms or Seequent’s policies
- Users are encouraged to review Leapfrog’s terms of use before integrating Pollywog into commercial or corporate environments
- The author is not responsible for any misuse of the tool that may breach Seequent’s licensing terms


## Installation

### From PyPI (Recommended)

```bash
pip install lf_pollywog
```

### From GitHub (Latest Development Version)

```bash
pip install git+https://github.com/endarthur/pollywog.git
```

### Try in Your Browser (No Installation)

Try Pollywog without installing anything using **JupyterLite**: [https://endarthur.github.io/pollyweb](https://endarthur.github.io/pollyweb)

> **Note**: JupyterLite runs in your browser and has limitations (no file system access, limited libraries). Files are stored in browser memory and won't persist if you clear your cache. Download your work regularly! For production use, preferably install locally.

## Usage Examples

### 1. Reading and Writing `.lfcalc` Files

```python
from pollywog.core import CalcSet, Number

# Read existing file
calcset = CalcSet.read_lfcalc("path/to/file.lfcalc")

# Modify calculations
calcset.items.append(Number("new_calc", "[Au] * 2"))

# Export modified version
calcset.to_lfcalc("output.lfcalc")
```

### 2. Creating Calculations from Scratch

```python
from pollywog.core import Number, CalcSet

calcset = CalcSet([
    Number("Au_clean", "clamp([Au], 0)",
           comment_equation="Remove negative values"),
    Number("Au_log", "log([Au_clean] + 1e-6)",
           comment_equation="Log transform for kriging"),
])

calcset.to_lfcalc("drillhole_preprocessing.lfcalc")
```

### 3. Using Helper Functions

Helpers can return either complete calculations or just expressions for composition:

```python
from pollywog.helpers import WeightedAverage, Product, CategoryFromThresholds
from pollywog.core import CalcSet, Number

calcset = CalcSet([
    # With name: Returns complete Number object
    WeightedAverage(
        variables=["Au_oxide", "Au_sulfide", "Au_transition"],
        weights=["prop_oxide", "prop_sulfide", "prop_transition"],
        name="Au_composite",
        comment="Domain-weighted gold grade"
    ),
    
    # Calculate gold equivalent (Ag and Cu converted to Au)
    Number("AuEq",
        "[Au_composite] + ([Ag_composite] * 0.011) + ([Cu_composite] * 1.5)",
        comment_equation="Gold equivalent grade (Ag/91, Cu*1.5 for price ratio)"
    ),
    
    # Without name: Returns expression for composition
    # Calculate net smelter return (NSR) per tonne
    Number("NSR_per_tonne",
        f"{Product(['Au_composite', '1800', '0.88'])} + "  # Au: price $1800/oz, 88% recovery
        f"{Product(['Ag_composite', '22', '0.75'])} + "    # Ag: price $22/oz, 75% recovery  
        f"{Product(['Cu_composite', '3.5', '0.85'])}"      # Cu: price $3.5/lb, 85% recovery
    ),
    
    # Classify by gold equivalent grade
    CategoryFromThresholds(
        variable="AuEq",
        thresholds=[0.5, 2.0],
        categories=["waste", "low_grade", "high_grade"],
        name="ore_class"
    ),
])

calcset.to_lfcalc("resource_model.lfcalc")
```

### 4. Machine Learning Model Conversion

Deploy machine learning models directly in Leapfrog:

```python
from pollywog.conversion.sklearn import convert_tree, convert_forest
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from pollywog.core import CalcSet
import numpy as np

# Training data: Au grade, Cu grade, grind size (P80)
X = np.array([[1.2, 0.3, 75], [0.8, 0.5, 100], [2.0, 0.2, 75]])
y = np.array([0.88, 0.82, 0.91])  # Recovery values

# Train and convert decision tree
model = DecisionTreeRegressor(max_depth=3, random_state=42)
model.fit(X, y)

recovery_calc = convert_tree(
    model, 
    ["Au_composite", "Cu_composite", "P80"], 
    "Au_recovery_predicted"
)

# Export to Leapfrog
CalcSet([recovery_calc]).to_lfcalc("ml_recovery_model.lfcalc")
```

### 5. Domain-Based Calculations

```python
from pollywog.core import CalcSet, Number, If
from pollywog.helpers import WeightedAverage

domains = ["oxide", "transition", "sulfide"]
metals = ["Au", "Ag", "Cu"]

# Domain-weighted grades for all metals
calcset = CalcSet([
    WeightedAverage(
        variables=[f"{metal}_{domain}" for domain in domains],
        weights=[f"prop_{domain}" for domain in domains],
        name=f"{metal}_composite",
        comment=f"Domain-weighted {metal} grade"
    )
    for metal in metals
])

# Apply domain-specific recovery
# Note: If objects require a list since they are separate structures
calcset.items.append(
    Number("Au_recovered", [
        If([
            ("[domain] = 'oxide'", "[Au_composite] * 0.92"),
            ("[domain] = 'transition'", "[Au_composite] * 0.85"),
            ("[domain] = 'sulfide'", "[Au_composite] * 0.78"),
        ], otherwise=["[Au_composite] * 0.75"])
    ])
)

calcset.to_lfcalc("multi_domain_workflow.lfcalc")
```

### 6. Querying CalcSets

Filter calculations like pandas DataFrames:

```python
# Select items by name pattern
au_calcs = calcset.query('name.startswith("Au")')

# Use external variables
metals_of_interest = ["Au", "Ag"]
selected = calcset.query('any(name.startswith(m) for m in @metals_of_interest)')

# Complex queries
filtered = calcset.query('len(expression) > 1 and "log" in name')
```

- Use item attributes (e.g., `name`, `item_type`) in expressions.
- Reference external variables using `@var` syntax (e.g., `name.startswith(@prefix)`).
- Supported helpers: `len`, `any`, `all`, `min`, `max`, `sorted`, `re`, `str`.

## Documentation

📚 **Full documentation**: [https://pollywog.readthedocs.io](https://pollywog.readthedocs.io/en/latest/)

- **[Getting Started](https://pollywog.readthedocs.io/en/latest/getting_started.html)** – Installation and first steps
- **[Tutorial for Resource Geologists](https://pollywog.readthedocs.io/en/latest/geologist_tutorial.html)** – For non-programmers familiar with Leapfrog
- **[Tutorials](https://pollywog.readthedocs.io/en/latest/tutorials.html)** – Complete workflow examples
- **[Expression Syntax](https://pollywog.readthedocs.io/en/latest/expression_syntax.html)** – Leapfrog expression reference
- **[Workflow Patterns](https://pollywog.readthedocs.io/en/latest/workflow_patterns.html)** – Common patterns and recipes
- **[Helper Functions](https://pollywog.readthedocs.io/en/latest/helpers_guide.html)** – Helper function guide
- **[Best Practices](https://pollywog.readthedocs.io/en/latest/best_practices.html)** – Production recommendations
- **[API Reference](https://pollywog.readthedocs.io/en/latest/api_reference.html)** – Complete API documentation

## License

MIT License – See [LICENSE](LICENSE) file for details.

## Contributions

Contributions are very welcome!
If you'd like to collaborate on Pollywog, whether through bug fixes, feature enhancements, new use cases, or documentation, please follow these steps:

- Fork the repository
- Create a feature branch (git checkout -b feature-name)
- Make your changes and commit (git commit -m 'Add new feature')
- Submit a pull request with a clear explanation of your changes

Before contributing, please:
- Ensure your changes align with the project’s goals
- Maintain consistent code style
- Test your modifications whenever possible
- Though It's ok to use LLMs to help write code or documentation, please review and understand all contributions to ensure quality and accuracy.

Feel free to open an issue if you have questions or suggestions.

## Acknowledgements

Thanks to Debora Roldão for helping with organization of the project, documentation and design, Eduardo Takafuji for the initial discussion of the feasability of this all those years ago and Jessica da Matta for support and sanity checks along the way.

## Links

- 📘 **Documentation**: https://pollywog.readthedocs.io
- 💻 **GitHub**: https://github.com/endarthur/pollywog
- 🚀 **Try Online**: https://endarthur.github.io/pollyweb
- 📦 **PyPI**: https://pypi.org/project/lf-pollywog/
- 🐛 **Issues**: https://github.com/endarthur/pollywog/issues
- 📖 **Examples**: [examples/](https://github.com/endarthur/pollywog/tree/main/examples) folder
