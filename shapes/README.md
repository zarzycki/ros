# Shapefiles

To add shapefiles, the directory needs to be named the same as the shapefiles contained within it. See the ones packaged with the repository for examples.

As of 6/2024, to acquire USGS HUC shapefiles, go to:

```
https://apps.nationalmap.gov/downloader/
```

and search for the HUC you are interested in. Download the corresponding `.zip` file and unpack. The WBDHUx.* files are what you are after, with the trailing integer representing the HUC level (e.g., WBDHU2 would be the two digit "region" (e.g., 18 for California) while WBDHU4 would be the four digit "subregion" (e.g., 1802 for Sacramento River Basin).

See also [Wikipedia](https://en.wikipedia.org/wiki/Hydrologic_unit_system_(United_States)).