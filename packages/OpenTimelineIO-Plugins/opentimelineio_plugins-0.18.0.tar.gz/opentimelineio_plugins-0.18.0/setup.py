# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='opentimelineio-plugins',
    version='0.18.0',
    description='OpenTimelineIO with batteries included plug-ins.',
    long_description='# OpenTimelineIO-Plugins\n\n<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenTimelineIO/main/docs/_static/OpenTimelineIO@3xLight.png">\n  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenTimelineIO/main/docs/_static/OpenTimelineIO@3xDark.png">\n  <img alt="OpenTimelineIO Logo" src="https://raw.githubusercontent.com/AcademySoftwareFoundation/OpenTimelineIO/main/docs/_static/OpenTimelineIO@3xDark.png">\n</picture>\n\n[OpenTimelineIO](https://opentimeline.io) is an interchange format and API for\neditorial cut information.\n\nThis package is a convenience includes both OpenTimelineIO and a set of plugins\nmaintained by the OpenTimelineIO community that are commonly used with the\nlibrary.\n\n## Support\n\nThe included plugins are part of the OpenTimelineIO project but may be supported\ndifferently than the OpenTimelineIO core.\n\nThis may include:\n\n- Repos primarily maintained by community members with OpenTimelineIO core team members only providing guidance\n- Repos that aren\'t actively maintained\n\nPlease consult READMEs in individual subproject repos to learn more about their\nmaintainance and support.\n\nLinks\n-----\n\n* Main web site: http://opentimeline.io/\n* Documentation: https://opentimelineio.readthedocs.io/\n* Main Project GitHub: https://github.com/AcademySoftwareFoundation/OpenTimelineIO\n* OpenTimelineIO-Plugins Github: https://github.com/OpenTimelineIO/OpenTimelineIO-Plugins\n* [Discussion group](https://lists.aswf.io/g/otio-discussion)\n* [Slack channel](https://academysoftwarefdn.slack.com/messages/CMQ9J4BQC)\n  * To join, create an account here first: https://slack.aswf.io/\n* [Presentations](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/wiki/Presentations)\n',
    author_email='Contributors to the OpenTimelineIO project <otio-discussion@lists.aswf.io>',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Display',
        'Topic :: Multimedia :: Video :: Non-Linear Editor',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'opentimelineio==0.18.0',
        'otio-aaf-adapter',
        'otio-ale-adapter',
        'otio-burnins-adapter',
        'otio-cmx3600-adapter',
        'otio-fcp-adapter',
        'otio-maya-sequencer-adapter',
        'otio-svg-adapter',
        'otio-xges-adapter',
    ],
    packages=[
        'opentimelineio_plugins',
    ],
)
