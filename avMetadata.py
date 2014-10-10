from genericpath import getsize
import hashlib
from os.path import splitext
from re import findall, DOTALL,compile, MULTILINE, search
from xml.dom.minidom import parseString

__author__ = 'Henry Borchers'
from subprocess import Popen, PIPE, STDOUT
GET_JSON_COMMAND = 'ffprobe -print_format xml -show_streams'

VALID_VIDEO_FILE_EXTENSIONS =['.avi', '.mov', '.mp4', '.mpeg', '.mpg', '.mkv']
VALID_AUDIO_FILE_EXTENSIONS =['.wav', '.mp3', '.ogg']


class AVMetadata():
    def __init__(self, fileName):
        self.fileName = fileName
        command = GET_JSON_COMMAND.split()
        command.append(self.fileName)
        p = Popen(command, stdout=PIPE, stderr=STDOUT, bufsize=0)
        rawdata = p.communicate()[0]
        self.fileXML = search('^(<\?xml).*(</ffprobe>)', rawdata, DOTALL).group(0)
        self.xmlDom = parseString(self.fileXML)
        print "done"
    def getFormat(self, file):

        #check if it's an audio format
        for extension in VALID_AUDIO_FILE_EXTENSIONS:
            if extension in file:
                return "audio"

        #check if it's a video format
        for extension in VALID_VIDEO_FILE_EXTENSIONS:
            if extension in file:
                return "video"
        return "unknown"

    def sizeof_human(self, num):
        num = int(num)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def validateFile(self):
        validation = True
    # check file extensions
        validExtension = False
        for extension in VALID_VIDEO_FILE_EXTENSIONS:
            if splitext(self.fileName)[1] == extension:
                validExtension = True
                break
        for extension in VALID_AUDIO_FILE_EXTENSIONS:
            # print type(extension)
            if splitext(self.fileName)[1] == extension:
                validExtension = True
                break
        if validExtension == False:
            validation = False

        return(validation)

    def getXML(self):
        return self.fileXML


    def getXMLDom(self):
        return self.xmlDom

    def getJSON(self):

        pass

    def test(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            print stream.getAttribute("codec_type")

    def getTotalRunningTime(self):
        pass

    def getAudioSampleRate(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "audio":
                return int(stream.getAttribute("sample_rate"))

    def getAudioChannels(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "audio":
                return int(stream.getAttribute("channels"))

    def getAudioCodec(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "audio":
                return stream.getAttribute("codec_name")

    def getAudioCodecLongName(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "audio":
                return stream.getAttribute("codec_long_name")

    def getAudioBitDepth(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "audio":
                rawdata = stream.getAttribute("sample_fmt")
                if rawdata == "s16p": return 16

    def getVideoCodec(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return stream.getAttribute("codec_name")
    def getVideoCodecLongName(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return stream.getAttribute("codec_long_name")

    def getVideoCodecTagString(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return stream.getAttribute("codec_tag_string")
    def getVideoCodecTag(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return stream.getAttribute("codec_tag")

    def getVideoFrameRate(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                rawFramerate = search('(.*)/(.*)', stream.getAttribute("avg_frame_rate"))
                frameRate = float(rawFramerate.group(1))/float(rawFramerate.group(2))
                return frameRate

    def getVideoColorSpace(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return stream.getAttribute("pix_fmt")

    def getVideoBitRate(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return int(stream.getAttribute("bit_rate"))

    def getVideoBitRateH(self):
        return self.sizeof_human(self.getVideoBitRate())

    def getVideoResolution(self):
        return str(self.getVideoResolutionHeight()) + "x" + str(self.getVideoResolutionWidth())

    def getVideoResolutionHeight(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return int(stream.getAttribute("height"))

    def getVideoResolutionWidth(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return int(stream.getAttribute("width"))

    def getFileSize(self):
        return getsize(self.fileName)

    def getFileSizeH(self):
        return self.sizeof_human(getsize(self.fileName))

    def getMD5(self):
        self.md5 = hashlib.md5()
        with open(self.fileName,'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                self.md5.update(chunk)
        return self.md5.hexdigest()

    def getSHA1(self):
        #TODO fix SHA1 checksum
        self.sha1 = hashlib.sha1()
        with open(self.fileName,'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                self.sha1.update(chunk)

        return self.sha1.hexdigest()
