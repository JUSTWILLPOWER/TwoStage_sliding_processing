class RadarScan():
  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       header,point_id,x,y,z,range,velocity,doppler_bin,bearing,intensity

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(RadarScan, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.header is None:
        self.header = ''
      if self.point_id is None:
        self.point_id = 0
      if self.x is None:
        self.x = 0.
      if self.y is None:
        self.y = 0.
      if self.z is None:
        self.z = 0.
      if self.range is None:
        self.range = 0.
      if self.velocity is None:
        self.velocity = 0.
      if self.doppler_bin is None:
        self.doppler_bin = 0
      if self.bearing is None:
        self.bearing = 0.
      if self.intensity is None:
        self.intensity = 0.
    else:
      self.header = ''
      self.point_id = 0
      self.x = 0.
      self.y = 0.
      self.z = 0.
      self.range = 0.
      self.velocity = 0.
      self.doppler_bin = 0
      self.bearing = 0.
      self.intensity = 0.
