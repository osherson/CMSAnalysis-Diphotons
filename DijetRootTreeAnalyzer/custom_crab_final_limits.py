def custom_crab(config):
  print '>> Customising the crab config'
 
  config.section_('General')

  config.General.workArea = 'HybridNew_RPV'

  config.section_("Site")

  config.Site.storageSite = 'T3_US_Rutgers'

  config.section_("JobType")

  config.JobType.allowUndistributedCMSSW = True

  config.section_("Data")

  config.Data.outLFNDirBase = '/store/user/thu/EOS'
  # config.Data.outLFNDirBase = '/store/group/phys_exotica/dijet/Dijet13TeV/ilias/HybridNew/13_slices_Envelope_alpha0p11'
#  config.Data.outLFNDirBase = '/store/group/phys_jetmet/ilias/4jets/crab_test'
#  config.Data.unitsPerJob = 50
#  config.Data.totalUnits = 4
