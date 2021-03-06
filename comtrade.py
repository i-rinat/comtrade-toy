import datetime
import struct
import os

class NotImplemetedException(Exception): pass
class NotExpectedException(Exception): pass

class Channel:
    def __repr__(self):
        return '<' + ', '.join([str(q) + ':' + str(self.__dict__[q]) for q in self.__dict__]) + '>'
    def __init__(self, line=None, ctype='A'):
        if ctype == 'A':
            self.id, self.name, self.phase, self.component, self.units, \
                self.a, self.b, self.skew, self.min, self.max = \
                line.split(',')[0:10]
            self.id = int(self.id)
            self.name = self.name.strip()
            self.component = self.component.strip()
            self.units = self.units.strip()
            self.a = float(self.a)
            self.b = float(self.b)
            self.skew = float(self.skew)
            self.min = int(self.min)
            self.max = int(self.max)
        elif ctype == 'D':
            self.id, self.name, self.normalstate = line.split(',')[0:3]
            self.id = int(self.id)
            self.name = self.name.strip()
            self.normalstate = int(self.normalstate)
        else:
            raise NotExpectedException("Expected ctype to by either 'A' or 'D'")
        self.data = []
        self.ctype = ctype

class OscReader:
    def __init__(self, fname=None):
        if fname is not None:
            self.open(fname)

    def open(self, fname):
        self.parse_cfg(fname)
        self.parse_dat(fname[0:-4]+'.dat')

    def parse_cfg(self, fname):
        f_meta = open(fname, 'r')

        # station name and id
        line = f_meta.readline().strip()
        line = line.split(',')
        std_year = 1991
        if len(line) == 3:
            self.station_name, self.station_id, std_year = line
            std_year = int(std_year)
        else:
            self.station_name, self.station_id = line
        if std_year != 1991:
            raise NotImplemetedException("Other than 1991 not implemented")

        # channel count
        line = f_meta.readline().strip()
        self.channel_count, type1, type2 = line.split(',')
        self.channel_count = int(self.channel_count)
        if type1[-1] != 'A': raise NotExpectedException("Expected analog channels first")
        if type2[-1] != 'D': raise NotExpectedException("Expected discrete channels second")
        self.channel_count_a = int(type1[0:-1])
        self.channel_count_d = int(type2[0:-1])
        if self.channel_count_a + self.channel_count_d != self.channel_count:
            raise NotExpectedException("A+D channel count do not match total")

        # channels description
        self.channel = {}
        for idx in range(0, self.channel_count_a):
            line = f_meta.readline().strip()
            channel = Channel(line, 'A')
            self.channel[channel.id] = channel
        for idx in range(0, self.channel_count_d):
            line = f_meta.readline().strip()
            channel = Channel(line, 'D')
            self.channel[channel.id] = channel

        # line frequency
        line = f_meta.readline().strip()
        self.line_frequency = int(line)

        # sample rates
        line = f_meta.readline().strip()
        self.n_rates = int(line)
        if (self.n_rates != 1):
            raise NotImplemetedException("More than one sample rate handling is not implemented")
        for idx in range(0, self.n_rates):
            line = f_meta.readline().strip()
            self.sample_rate, self.sample_count = line.split(',')
            self.sample_rate = int(self.sample_rate)
            self.sample_count = int(self.sample_count)

        # timestamps
        self.timestamp1 = f_meta.readline().strip()
        self.timestamp2 = f_meta.readline().strip()

        # file type
        line = f_meta.readline().strip()
        if line != 'BINARY':
            raise NotImplemetedException("Only BINARY .dat supported")
        self.filetype = 'BINARY'

        f_meta.close()

    def parse_dat(self, fname_dat):
        f_data = open(fname_dat, 'rb')

        # each analog channel takes two bytes
        sample_len = self.channel_count_a * 2
        # status channels stored by tuples of 16
        sample_len += 2 * ((self.channel_count_d - 1)//16 + 1)
        # sample number and timestamp consist of four bytes each
        sample_len += 4 + 4

        f_size = os.path.getsize(fname_dat)
        while f_data.tell() < f_size:
            sample_number, = struct.unpack('i', f_data.read(4))
            sample_timestamp, = struct.unpack('i', f_data.read(4))
            ch = 1
            for idx in range(0, self.channel_count_a):
                sample, = struct.unpack('h', f_data.read(2))
                channel = self.channel[ch]
                channel.data.append(channel.a * sample + channel.b)
                ch += 1
            for idx in range(0, (self.channel_count_d -1)//16 +1):
                sample, = struct.unpack('H', f_data.read(2))
                locidx = 0
                while locidx < 16 and ch <= self.channel_count:
                    bit = sample & 1
                    self.channel[ch].data.append(bit)
                    sample >>= 1
                    ch += 1
                    locidx += 1

        f_data.close()
