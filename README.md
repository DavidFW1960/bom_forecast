[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This Custom Integration is now deprecated and will eventually be removed from HACS and may or may not continue to work (unless BOM changes something)
The reason for this is that Home Assistant as of version 0.117.0 have removed the BOM Sensor and Radar.

Brendan who originally wrote this component has now made a NEW BOM component that replaces both the BOM Sensor AND this FTP component. His new component uses a BOM API.

Please download the new [BOM Component by Brendan here] (https://github.com/bremor/bureau_of_meteorology)
and the [Radar Card by Simon here] (https://github.com/theOzzieRat/bom-radar-card)

You can add both to HACS by adding a custom repository. (Integration for BOM and Lovelace for Radar)

Note that my custom animated card works with the new component but will require some changes to the configuration. I will detail this in the repo for the card.