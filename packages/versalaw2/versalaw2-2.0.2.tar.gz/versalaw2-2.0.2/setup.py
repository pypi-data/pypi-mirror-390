from setuptools import setup, find_packages

setup(
    name="versalaw2",
    version="2.0.2",  # ✅ NAIKKAN VERSION
    packages=find_packages(),
    package_data={
        'versalaw2': [
            'legal_knowledge/advanced_cases/*.md',
            'legal_knowledge/law_library/*.md',
            'legal_knowledge/supreme_analysis/*.md',
        ],
    },
    include_package_data=True,
    python_requires=">=3.7",
)
