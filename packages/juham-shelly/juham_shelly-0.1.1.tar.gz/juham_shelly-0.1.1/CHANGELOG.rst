Changelog
=========


[0.1.1] - November 8, 2025
--------------------------
- *ShellyDHT22* handles 'sys' message silently.
- *test_shellymotion.py* unit test added.



[0.1.0] - April 17, 2025
------------------------
* Updated to comply with the new SPDX expression for packaging standards
* Development Status elevated to Alpha
  

[0.0.9] - April 08, 2025
------------------------

- Fixed random crashes in the following shellydht22 class due to exception from float(humidity).
  
   .. code-block:: python

      sensor_id = key.split(":")[1]
      humidity = float(value[unit]) # sometimes None


[0.0.6] - March 16, 2025
------------------------

- Two new unit test classes added


[0.0.5] - January 19, 2025
--------------------------

- Documentation refactored

- GitLab migration


[0.0.1] - January 19, 2025
--------------------------

- **First release:** 

