from setuptools import setup, find_packages

setup(
    name="paytm-verifier",
    version="1.0.3",
    author="UdayScripts",
    author_email="support@udayscripts.in",
    description="Verify Paytm merchant payments using MID and Order ID.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Uday-x-ai/paytm-verifier",
    project_urls={
        "Telegram": "https://t.me/UdayScripts"
    },
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires=">=3.7"
)
