# backgrounds

A set tools for stochastic gravitational wave backgrounds data analysis.

## Documentation

A documentation is available on Github pages: https://qbaghi.pages.in2p3.fr/backgrounds

## Dependencies

Backgrounds requires LISA Constants and LISA GW Response from the LISA Simulation suite, which can be installed as
```
pip install git+https://@gitlab.in2p3.fr/lisa-simulation/constants.git@latest
pip install git+https://gitlab.in2p3.fr/lisa-simulation/gw-response.git@latest
```
To run the scripts in the tests folder it is recommanded to install the packages listed in the requirements:
```
pip install --no-cache-dir -r requirements.txt
```

## Installation

### Released version

Simply run
```
pip install backgrounds
```

### Development version

You need to be part of the LISA Consortium and have access to the IN2P3 Gitlab to access the
development version. This will change in the future.

Please clone the repository and do a manual installation:
```
git clone git@gitlab.in2p3.fr:qbaghi/backgrounds.git
cd backgrounds
pip install -e .
```