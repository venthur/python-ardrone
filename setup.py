# ===========================================================================
#
#  COPYRIGHT 2013 Brain Corporation.
#  All rights reserved. Brain Corporation proprietary and confidential.
#
#  The party receiving this software directly from Brain Corporation
#  (the "Recipient" ) may use this software and make copies thereof as
#  reasonably necessary solely for the purposes set forth in the agreement
#  between the Recipient and Brain Corporation ( the "Agreement" ). The
#  software may be used in source code form
#  solely by the Recipient's employees. The Recipient shall have no right to
#  sublicense, assign, transfer or otherwise provide the source code to any
#  third party. Subject to the terms and conditions set forth in the Agreement,
#  this software, in binary form only, may be distributed by the Recipient to
#  its customers. Brain Corporation retains all ownership rights in and to
#  the software.
#
#  This notice shall supercede any other notices contained within the software.
# =============================================================================

from setuptools import setup, find_packages


setup(
    name='mtools',
    author='Brain Corporation',
    author_email='sinyavskiy@braincorporation.com',
    url='https://github.com/braincorp/mtools',
    long_description='',
    version='dev',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[])
