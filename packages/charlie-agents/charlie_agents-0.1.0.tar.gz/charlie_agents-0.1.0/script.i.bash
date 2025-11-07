cd /Users/henriquemoody/opt/personal/charlie

# Clear caches
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache build dist

# Reinstall
pip uninstall -y charlie
pip install -e .

# Run tests
python3 -m pytest -v