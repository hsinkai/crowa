#!/package/python-2.7.3/bin/python
# -*- coding: utf-8 -*-

import sys
import os


sys.path.append('/package/apma/lib/python2.7/site-packages')	# SETUP-REPLACE: LIBRARY-PATH

INSTALL_BASE = '/package/apma'	# SETUP-REPLACE: INSTALL-PREFIX

sys.path.append(os.path.join(INSTALL_BASE, "lib"))

# ### change above path



if __name__ == "__main__":
	db_config_path = os.path.join(INSTALL_BASE, "etc", 'db_config.yaml')

	if 2 > len(sys.argv):
		print "Argument: [CONFIG_FILE]"
		sys.exit(1)

	from opra.core import expectop
	from opra import messagemap

	ret = expectop.run_expect_generation(db_config_path, sys.argv[1:])

	if 0 != ret:
		errmsg = messagemap.EXPECTITEM_GEN_MESSAGE.get(ret, "Unknown Error")
		sys.stderr.write("ERR: %r\n" % (errmsg,))
		sys.exit(0 - ret)
	else:
		sys.exit(0)
# <<< if __name__ == "__main__":



# vim: ts=4 sw=4 foldmethod=marker ai nowrap
