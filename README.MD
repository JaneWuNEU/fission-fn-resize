## Fission function resize

## Overview

This project targets at adjust Fission-based functions' CPU cores/memory at runtime (function resize).

Functions in Fission are sorted as newdeploy based and poolmgr based functions.

For **newdeploy**-based functions, their available resources are determined by fission fn-level configurations, rather than that of fission env-level. On the other hand, available resources for poolmgr-based functions are controlled by fission env-level configurations. Thus, their resizing needs to be implemented respectively.

## Newdeploy-based functions

we can depend on `update` to implement resizing. Notably, prior to udpating, we need to ensure that the env required by this function has been created; meanwhile, there exists one fn at least to support the update. More details please refer to `update_size_for_newdeploy` in main.py.

## Poolmgr-based functions

Availalbe resources for this kind of functions are determined by env-level configurations. Moreover, it is required to delete the outdated env and the corresponding fn firstly. Otherwise, the lastest configuration will not take effect. More details please refer to `update_size_for_poolmgr` in main.py
