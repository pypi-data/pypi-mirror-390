from setuptools import setup, find_namespace_packages
import os
import pathlib

here = pathlib.Path(__file__).parent.resolve()
about = {}

# Read version from version.py
with open(os.path.join(here, "livekit-plugins-talklabs", "livekit", "plugins", "talklabs", "version.py"), "r") as f:
    exec(f.read(), about)

# Read README
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="livekit-plugins-talklabs",
    version=about["__version__"],
    description="TalkLabs TTS plugin for LiveKit Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/talklabs/livekit-plugins-talklabs",
    author="TalkLabs",
    author_email="support@talklabs.com.br",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="livekit, webrtc, realtime, tts, text-to-speech, talklabs",
    package_dir={"": "livekit-plugins-talklabs"},
    packages=find_namespace_packages(
        where="livekit-plugins-talklabs",
        include=["livekit.plugins.talklabs", "livekit.plugins.talklabs.*"],
    ),
    python_requires=">=3.9",
    install_requires=[
        "livekit-agents>=1.2.0",
        "talklabs>=2.0.0",  # TalkLabs SDK
    ],
    package_data={
        "livekit.plugins.talklabs": ["py.typed"],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/talklabs/livekit-plugins-talklabs/issues",
        "Source": "https://github.com/talklabs/livekit-plugins-talklabs",
        "Documentation": "https://docs.talklabs.com.br",
    },
)