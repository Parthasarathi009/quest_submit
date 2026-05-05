[metadata]
name = rearc-quest
version = 1.0.0
description = Rearc Data Quest - Data Pipeline Implementation
author = Your Name
author_email = your.email@example.com
url = https://github.com/yourname/rearc-quest

[options]
packages = find:
python_requires = >=3.11
install_requires =
    boto3>=1.26.0
    requests>=2.28.0
    pandas>=2.0.0
    python-dotenv>=0.21.0

[options.extras_require]
dev =
    pytest>=7.0
    pytest-cov>=4.0
    black>=23.0
    flake8>=6.0
    mypy>=1.0

[options.packages.find]
exclude =
    tests
    docs
