<!--In production at [https://synapse.ksu.edu/](https://synapse.ksu.edu)
<br>
-->

<div align="center">
  <img src="https://raw.githubusercontent.com/cnap-cobre/synapse/master/logo.png" alt="Synapse Logo" width="450">
  <br><br>
  Dataverse IO via Globus
  <br><br>
</div>

<!--
[![Build Status](https://travis-ci.org/cnap-cobre/synapse.svg?branch=master)](https://travis-ci.org/cnap-cobre/synapse)
[![Greenkeeper badge](https://badges.greenkeeper.io/cnap-cobre/synapse.svg)](https://greenkeeper.io/)
[![Documentation Status](https://readthedocs.org/projects/cnap-synapse/badge/?version=latest)](http://cnap-synapse.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/cnap-cobre/synapse/badge.svg)](https://coveralls.io/github/cnap-cobre/synapse)

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fcnap-cobre%2Fsynapse.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fcnap-cobre%2Fsynapse?ref=badge_shield)
[![Dependency Freshness](https://david-dm.org/cnap-cobre/synapse/status.svg?path=frontend)](https://david-dm.org/cnap-cobre/synapse?path=frontend)
[![Maintainability](https://api.codeclimate.com/v1/badges/51341d034ff8d6c600c6/maintainability)](https://codeclimate.com/github/cnap-cobre/synapse/maintainability)
-->



Synapse is a browser-based (Flask) interface for transferring data between a [Dataverse](https://dataverse.org/) installation utilizing [Globus](https://www.globus.org/).
This is currently accomplished by transferring the data into a staging area "on" the Dataverse server, then use API calls for actually importing them in.
In the future we plan on taking very large files and only importing in a placeholder. Getting that handle, we will replace the file that the import created, with the actual file, then update the DB with the new filesize.


To Run Flask environment directly with ngrok (dev only): ngrok http -host-header=rewrite localhost:5000

<!--
## Documentation

All Docs:  https://cnap-synapse.readthedocs.io/en/latest/

User Docs:  https://cnap-synapse.readthedocs.io/en/latest/user/

Developer Docs:  https://cnap-synapse.readthedocs.io/en/latest/developer/

Design Docs:  https://cnap-synapse.readthedocs.io/en/latest/design/

Deployment Docs:  https://cnap-synapse.readthedocs.io/en/latest/deployment/
-->
## Contributors
- Gerrick Teague
- Kevin Dice
- Lauren Lynch
- Gabe Maddex

Submitting a PR?  Add yourself to this list.

## License

Synapse is licensed under the [MIT License](https://tldrlegal.com/license/mit-license).

You are free to do anything with this software except hold its creators liable.  You must include the copyright notice and MIT License in all copies or substantial uses of the work.  See [LICENSE.md](./LICENSE.md) for the full license text.

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fcnap-cobre%2Fsynapse.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fcnap-cobre%2Fsynapse?ref=badge_large)
