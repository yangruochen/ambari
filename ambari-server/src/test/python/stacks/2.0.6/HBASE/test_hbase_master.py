#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from mock.mock import MagicMock, patch
from stacks.utils.RMFTestCase import *

@patch("os.path.exists", new = MagicMock(return_value=True))
class TestHBaseMaster(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "HBASE/0.96.0.2.0/package"
  STACK_VERSION = "2.0.6"

  def test_configure_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "configure",
                   config_file="default.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    
    self.assert_configure_default()
    self.assertNoMoreResources()

  def test_start_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "start",
                   config_file="default.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    
    self.assert_configure_default()
    self.assertResourceCalled('Execute', '/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start master',
      not_if = 'ls /var/run/hbase/hbase-hbase-master.pid >/dev/null 2>&1 && ps -p `cat /var/run/hbase/hbase-hbase-master.pid` >/dev/null 2>&1',
      user = 'hbase'
    )
    self.assertNoMoreResources()
    
  def test_stop_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "stop",
                   config_file="default.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    
    self.assertResourceCalled('Execute', '/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop master',
        on_timeout = '! ( ls /var/run/hbase/hbase-hbase-master.pid >/dev/null 2>&1 && ps -p `cat /var/run/hbase/hbase-hbase-master.pid` >/dev/null 2>&1 ) || sudo -H -E kill -9 `cat /var/run/hbase/hbase-hbase-master.pid`',
        timeout = 30,
        user = 'hbase',
    )
    
    self.assertResourceCalled('Execute', 'rm -f /var/run/hbase/hbase-hbase-master.pid',
    )
    self.assertNoMoreResources()

  def test_decom_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                       classname = "HbaseMaster",
                       command = "decommission",
                       config_file="default.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('File', '/usr/lib/hbase/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/draining_servers.rb add host1',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/region_mover.rb unload host1',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/draining_servers.rb add host2',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/region_mover.rb unload host2',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertNoMoreResources()

  def test_decom_default_draining_only(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                       classname = "HbaseMaster",
                       command = "decommission",
                       config_file="default.hbasedecom.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('File', '/usr/lib/hbase/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', ' /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/draining_servers.rb remove host1',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertNoMoreResources()

  def test_configure_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "configure",
                   config_file="secured.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    
    self.assert_configure_secured()
    self.assertNoMoreResources()
    
  def test_start_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "start",
                   config_file="secured.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    
    self.assert_configure_secured()
    self.assertResourceCalled('Execute', '/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf start master',
      not_if = 'ls /var/run/hbase/hbase-hbase-master.pid >/dev/null 2>&1 && ps -p `cat /var/run/hbase/hbase-hbase-master.pid` >/dev/null 2>&1',
      user = 'hbase',
    )
    self.assertNoMoreResources()
    
  def test_stop_secured(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "stop",
                   config_file="secured.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('Execute', '/usr/lib/hbase/bin/hbase-daemon.sh --config /etc/hbase/conf stop master',
        on_timeout = '! ( ls /var/run/hbase/hbase-hbase-master.pid >/dev/null 2>&1 && ps -p `cat /var/run/hbase/hbase-hbase-master.pid` >/dev/null 2>&1 ) || sudo -H -E kill -9 `cat /var/run/hbase/hbase-hbase-master.pid`',
        timeout = 30,
        user = 'hbase',
    )

    self.assertResourceCalled('Execute', 'rm -f /var/run/hbase/hbase-hbase-master.pid',
    )
    self.assertNoMoreResources()

  def test_decom_secure(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                       classname = "HbaseMaster",
                       command = "decommission",
                       config_file="secured.json",
                       hdp_stack_version = self.STACK_VERSION,
                       target = RMFTestCase.TARGET_COMMON_SERVICES
    )

    self.assertResourceCalled('File', '/usr/lib/hbase/bin/draining_servers.rb',
                              content = StaticFile('draining_servers.rb'),
                              mode = 0755,
                              )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/hbase.headless.keytab hbase; /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/draining_servers.rb add host1',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertResourceCalled('Execute', '/usr/bin/kinit -kt /etc/security/keytabs/hbase.headless.keytab hbase; /usr/lib/hbase/bin/hbase --config /etc/hbase/conf org.jruby.Main /usr/lib/hbase/bin/region_mover.rb unload host1',
                              logoutput = True,
                              user = 'hbase',
                              )
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/etc/hbase',
      mode = 0755
    )
    self.assertResourceCalled('Directory', '/etc/hbase/conf',
      owner = 'hbase',
      group = 'hadoop',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase',
      owner = 'hbase',
      mode = 0775,
      recursive = True,
      recursive_permission = True
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase/local',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase/local/jars',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True,
    )
    self.assertResourceCalled('XmlConfig', 'hbase-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hbase-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hbase-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['hdfs-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('File', '/etc/hbase/conf/hbase-policy.xml',
      owner = 'hbase',
      group = 'hadoop'
    )
    self.assertResourceCalled('File', '/etc/hbase/conf/hbase-env.sh',
      owner = 'hbase',
      content = InlineTemplate(self.getConfig()['configurations']['hbase-env']['content']),
    )
    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/hadoop-metrics2-hbase.properties',
      owner = 'hbase',
      template_tag = 'GANGLIA-MASTER',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/regionservers',
      owner = 'hbase',
      template_tag = None,
    )
    self.assertResourceCalled('Directory', '/var/run/hbase',
      owner = 'hbase',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/var/log/hbase',
      owner = 'hbase',
      recursive = True,
    )
    self.assertResourceCalled('File',
                              '/etc/hbase/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='hbase',
                              content='log4jproperties\nline2'
    )
    self.assertResourceCalled('HdfsDirectory', 'hdfs://c6401.ambari.apache.org:8020/apps/hbase/data',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              owner = 'hbase',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', '/apps/hbase/staging',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              mode = 0711,
                              owner = 'hbase',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', None,
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              bin_dir = '/usr/bin',
                              action = ['create'],
                              )

  def assert_configure_secured(self):
    self.assertResourceCalled('Directory', '/etc/hbase',
      mode = 0755
    )
    self.assertResourceCalled('Directory', '/etc/hbase/conf',
      owner = 'hbase',
      group = 'hadoop',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase',
      owner = 'hbase',
      mode = 0775,
      recursive = True,
      recursive_permission = True
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase/local',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True
    )
    self.assertResourceCalled('Directory', '/hadoop/hbase/local/jars',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True,
    )
    self.assertResourceCalled('XmlConfig', 'hbase-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hbase-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hbase-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'hdfs',
      group = 'hadoop',
      conf_dir = '/etc/hadoop/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site']
    )
    self.assertResourceCalled('File', '/etc/hbase/conf/hbase-policy.xml',
      owner = 'hbase',
      group = 'hadoop',
    )
    self.assertResourceCalled('File', '/etc/hbase/conf/hbase-env.sh',
      owner = 'hbase',
      content = InlineTemplate(self.getConfig()['configurations']['hbase-env']['content']),
    )
    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/hadoop-metrics2-hbase.properties',
      owner = 'hbase',
      template_tag = 'GANGLIA-MASTER',
    )
    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/regionservers',
      owner = 'hbase',
      template_tag = None,
    )
    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/hbase_master_jaas.conf',
      owner = 'hbase',
      template_tag = None,
    )
    self.assertResourceCalled('Directory', '/var/run/hbase',
      owner = 'hbase',
      recursive = True,
    )
    self.assertResourceCalled('Directory', '/var/log/hbase',
      owner = 'hbase',
      recursive = True,
    )
    self.assertResourceCalled('File',
                              '/etc/hbase/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='hbase',
                              content='log4jproperties\nline2'
    )
    self.assertResourceCalled('HdfsDirectory', 'hdfs://c6401.ambari.apache.org:8020/apps/hbase/data',
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              owner = 'hbase',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', '/apps/hbase/staging',
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              mode = 0711,
                              owner = 'hbase',
                              bin_dir = '/usr/bin',
                              action = ['create_delayed'],
                              )
    self.assertResourceCalled('HdfsDirectory', None,
                              security_enabled = True,
                              keytab = '/etc/security/keytabs/hdfs.headless.keytab',
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = '/usr/bin/kinit',
                              bin_dir = '/usr/bin',
                              action = ['create'],
                              )

  def test_start_default_22(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/hbase_master.py",
                   classname = "HbaseMaster",
                   command = "start",
                   config_file="hbase-2.2.json",
                   hdp_stack_version = self.STACK_VERSION,
                   target = RMFTestCase.TARGET_COMMON_SERVICES)
    
    self.assertResourceCalled('Directory', '/etc/hbase',
      mode = 0755)

    self.assertResourceCalled('Directory', '/etc/hbase/conf',
      owner = 'hbase',
      group = 'hadoop',
      recursive = True)

    self.assertResourceCalled('Directory', '/hadoop/hbase',
      owner = 'hbase',
      mode = 0775,
      recursive = True,
      recursive_permission = True)

    self.assertResourceCalled('Directory', '/hadoop/hbase/local',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True)

    self.assertResourceCalled('Directory', '/hadoop/hbase/local/jars',
      owner = 'hbase',
      group = 'hadoop',
      mode=0775,
      recursive = True)

    self.assertResourceCalled('XmlConfig', 'hbase-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hbase-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hbase-site'])

    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hdfs-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site'])

    self.assertResourceCalled('XmlConfig', 'hdfs-site.xml',
                              owner = 'hdfs',
                              group = 'hadoop',
                              conf_dir = '/etc/hadoop/conf',
                              configurations = self.getConfig()['configurations']['hdfs-site'],
                              configuration_attributes = self.getConfig()['configuration_attributes']['hdfs-site'])

    self.assertResourceCalled('XmlConfig', 'hbase-policy.xml',
      owner = 'hbase',
      group = 'hadoop',
      conf_dir = '/etc/hbase/conf',
      configurations = self.getConfig()['configurations']['hbase-policy'],
      configuration_attributes = self.getConfig()['configuration_attributes']['hbase-policy'])

    self.assertResourceCalled('File', '/etc/hbase/conf/hbase-env.sh',
      owner = 'hbase',
      content = InlineTemplate(self.getConfig()['configurations']['hbase-env']['content']))

    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/hadoop-metrics2-hbase.properties',
      owner = 'hbase',
      template_tag = 'GANGLIA-MASTER')

    self.assertResourceCalled('TemplateConfig', '/etc/hbase/conf/regionservers',
      owner = 'hbase',
      template_tag = None)

    self.assertResourceCalled('Directory', '/var/run/hbase',
      owner = 'hbase',
      recursive = True)

    self.assertResourceCalled('Directory', '/var/log/hbase',
      owner = 'hbase',
      recursive = True)

    self.assertResourceCalled('File',
                              '/etc/hbase/conf/log4j.properties',
                              mode=0644,
                              group='hadoop',
                              owner='hbase',
                              content='log4jproperties\nline2')

    self.assertResourceCalled('HdfsDirectory', 'hdfs://nn1/apps/hbase/data',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              owner = 'hbase',
                              bin_dir = '/usr/hdp/current/hadoop-client/bin',
                              action = ['create_delayed'])

    self.assertResourceCalled('HdfsDirectory', '/apps/hbase/staging',
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              mode = 0711,
                              owner = 'hbase',
                              bin_dir = '/usr/hdp/current/hadoop-client/bin',
                              action = ['create_delayed'])

    self.assertResourceCalled('HdfsDirectory', None,
                              security_enabled = False,
                              keytab = UnknownConfigurationMock(),
                              conf_dir = '/etc/hadoop/conf',
                              hdfs_user = 'hdfs',
                              kinit_path_local = "/usr/bin/kinit",
                              bin_dir = '/usr/hdp/current/hadoop-client/bin',
                              action = ['create'])

    self.assertResourceCalled('Execute', '/usr/hdp/current/hbase-master/bin/hbase-daemon.sh --config /etc/hbase/conf start master',
      not_if = 'ls /var/run/hbase/hbase-hbase-master.pid >/dev/null 2>&1 && ps -p `cat /var/run/hbase/hbase-hbase-master.pid` >/dev/null 2>&1',
      user = 'hbase')

    self.assertNoMoreResources()

