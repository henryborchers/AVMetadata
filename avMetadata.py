__author__ = 'Henry Borchers'


from genericpath import getsize
import hashlib
from os.path import splitext
from re import findall, DOTALL,compile, MULTILINE, search
from xml.dom.minidom import parseString
from subprocess import Popen, PIPE, STDOUT


# Constants
GET_XML_COMMAND = 'ffprobe -print_format xml -show_streams'

VALID_VIDEO_FILE_EXTENSIONS =['.avi', '.mov', '.mp4', '.mpeg', '.mpg', '.mkv']
VALID_AUDIO_FILE_EXTENSIONS =['.wav', '.mp3', '.ogg']

COLORSPACES = {"yuv420p": "YUV",
                    "yuyv422": "YUYV",
                    "rgb24": "RGB",
                    "bgr24": "BGR",
                    "yuv422p": "YUV",
                    "yuv444p": "YUV",
                    "yuv410p": "YUV",
                    "yuv411p": "YUV",
                    "gray": "",
                    "monow": "",
                    "monob": "",
                    "pal8": "",
                    "yuvj420p": "YUVJ",
                    "yuvj422p": "YUVJ",
                    "yuvj444p": "YUVK",
                    "xvmcmc": "",
                    "xvmcidct": "",
                    "uyvy422": "UYVY",
                    "uyyvyy411": "UYYVYY",
                    "bgr8": "BGR",
                    "bgr4": "BGR",
                    "bgr4_byte": "BGR",
                    "rgb8": "RGB",
                    "rgb4": "RGB",
                    "rgb4_byte": "RGB",
                    "nv12": "",
                    "nv21": "",
                    "argb": "",
                    "rgba": "RGBA",
                    "abgr": "",
                    "bgra": "",
                    "gray16be": "",
                    "gray16le": "",
                    "yuv440p": "YUV",
                    "yuvj440p": "YUVJ",
                    "yuva420p": "YUVA",
                    "vdpau_h264": "",
                    "vdpau_mpeg1": "",
                    "vdpau_mpeg2": "",
                    "vdpau_wmv3": "",
                    "vdpau_vc1": "",
                    "rgb48be": "RGB",
                    "rgb48le": "RGB",
                    "rgb565be": "RGB",
                    "rgb565le": "RGB",
                    "rgb555be": "RGB",
                    "rgb555le": "RGB",
                    "bgr565be": "BGR",
                    "bgr565le": "BGR",
                    "bgr555be": "BGR",
                    "bgr555le": "BGR",
                    "vaapi_moco": "",
                    "vaapi_idct": "",
                    "vaapi_vld": "",
                    "yuv420p16le": "YUV",
                    "yuv420p16be": "YUV",
                    "yuv422p16le": "YUV",
                    "yuv422p16be": "YUV",
                    "yuv444p16le": "YUV",
                    "yuv444p16be": "YUV",
                    "vdpau_mpeg4": "",
                    "dxva2_vld": "",
                    "rgb444le": "RGB",
                    "rgb444be": "RGB",
                    "bgr444le": "BGR",
                    "bgr444be": "BGR",
                    "ya8": "",
                    "bgr48be": "BGR",
                    "bgr48le": "BGR",
                    "yuv420p9be": "YUV",
                    "yuv420p9le": "YUV",
                    "yuv420p10be": "YUV",
                    "yuv420p10le": "YUV",
                    "yuv422p10be": "YUV",
                    "yuv422p10le": "YUV",
                    "yuv444p9be": "YUV",
                    "yuv444p9le": "YUV",
                    "yuv444p10be": "YUV",
                    "yuv444p10le": "YUV",
                    "yuv422p9be": "YUV",
                    "yuv422p9le": "YUV",
                    "vda_vld": "",
                    "gbrp": "",
                    "gbrp9be": "",
                    "gbrp9le": "",
                    "gbrp10be": "",
                    "gbrp10le": "",
                    "gbrp16be": "",
                    "gbrp16le": "",
                    "yuva420p9be": "YUVA",
                    "yuva420p9le": "YUVA",
                    "yuva422p9be": "YUVA",
                    "yuva422p9le": "YUVA",
                    "yuva444p9be": "YUVA",
                    "yuva444p9le": "YUVA",
                    "yuva420p10be": "YUVA",
                    "yuva420p10le": "YUVA",
                    "yuva422p10be": "YUVA",
                    "yuva422p10le": "YUVA",
                    "yuva444p10be": "YUVA",
                    "yuva444p10le": "YUVA",
                    "yuva420p16be": "YUVA",
                    "yuva420p16le": "YUVA",
                    "yuva422p16be": "YUVA",
                    "yuva422p16le": "YUVA",
                    "yuva444p16be": "YUVA",
                    "yuva444p16le": "YUVA",
                    "vdpau": "",
                    "xyz12le": "",
                    "xyz12be": "",
                    "nv16": "",
                    "nv20le": "",
                    "nv20be": "",
                    "yvyu422": "",
                    "vda": "",
                    "ya16be": "",
                    "ya16le": "",
                    "rgba64be": "RGBA",
                    "rgba64le": "RGBA",
                    "bgra64be": "BGRA",
                    "bgra64le": "BGRA",
                    "0rgb": "",
                    "rgb0": "",
                    "0bgr": "",
                    "bgr0": "",
                    "yuva444p": "YUVA",
                    "yuva422p": "YUVA",
                    "yuv420p12be": "YUV",
                    "yuv420p12le": "YUV",
                    "yuv420p14be": "YUV",
                    "yuv420p14le": "YUV",
                    "yuv422p12be": "YUV",
                    "yuv422p12le": "YUV",
                    "yuv422p14be": "YUV",
                    "yuv422p14le": "YUV",
                    "yuv444p12be": "YUV",
                    "yuv444p12le": "YUV",
                    "yuv444p14be": "YUV",
                    "yuv444p14le": "YUV",
                    "gbrp12be": "GBRP",
                    "gbrp12le": "GBRP",
                    "gbrp14be": "GBRP",
                    "gbrp14le": "GBRP",
                    "gbrap": "",
                    "gbrap16be": "",
                    "gbrap16le": "",
                    "yuvj411p": "YUBJ",
                    "bayer_bggr8": "",
                    "bayer_rggb8": "",
                    "bayer_gbrg8": "",
                    "bayer_grbg8": "",
                    "bayer_bggr16le": "",
                    "bayer_bggr16be": "",
                    "bayer_rggb16le": "",
                    "bayer_rggb16be": "",
                    "bayer_gbrg16le": "",
                    "bayer_gbrg16be": "",
                    "bayer_grbg16le": "",
                    "bayer_grbg16be": ""}

CHROMA_SUB_SAMPLING= {"yuv420p": "4:2:0",
                    "yuyv422": "4:2:2",
                    "rgb24": "",
                    "bgr24": "",
                    "yuv422p": "4:2:2",
                    "yuv444p": "4:4:4",
                    "yuv410p": "4:1:0",
                    "yuv411p": "4:1:1",
                    "gray": "",
                    "monow": "",
                    "monob": "",
                    "pal8": "",
                    "yuvj420p": "4:2:0",
                    "yuvj422p": "4:2:2",
                    "yuvj444p": "4:4:4",
                    "xvmcmc": "",
                    "xvmcidct": "",
                    "uyvy422": "4:2:2",
                    "uyyvyy411": "4:1:1",
                    "bgr8": "",
                    "bgr4": "",
                    "bgr4_byte": "",
                    "rgb8": "",
                    "rgb4": "",
                    "rgb4_byte": "",
                    "nv12": "",
                    "nv21": "",
                    "argb": "",
                    "rgba": "",
                    "abgr": "",
                    "bgra": "",
                    "gray16be": "",
                    "gray16le": "",
                    "yuv440p": "4:4:0",
                    "yuvj440p": "4:4:0",
                    "yuva420p": "4:2:0",
                    "vdpau_h264": "",
                    "vdpau_mpeg1": "",
                    "vdpau_mpeg2": "",
                    "vdpau_wmv3": "",
                    "vdpau_vc1": "",
                    "rgb48be": "",
                    "rgb48le": "",
                    "rgb565be": "",
                    "rgb565le": "",
                    "rgb555be": "",
                    "rgb555le": "",
                    "bgr565be": "",
                    "bgr565le": "",
                    "bgr555be": "",
                    "bgr555le": "",
                    "vaapi_moco": "",
                    "vaapi_idct": "",
                    "vaapi_vld": "",
                    "yuv420p16le": "4:2:0",
                    "yuv420p16be": "4:2:0",
                    "yuv422p16le": "4:2:2",
                    "yuv422p16be": "4:2:2",
                    "yuv444p16le": "4:4:4",
                    "yuv444p16be": "4:4:4",
                    "vdpau_mpeg4": "",
                    "dxva2_vld": "",
                    "rgb444le": "4:4:4",
                    "rgb444be": "4:4:4",
                    "bgr444le": "4:4:4",
                    "bgr444be": "4:4:4",
                    "ya8": "",
                    "bgr48be": "",
                    "bgr48le": "",
                    "yuv420p9be": "4:2:0",
                    "yuv420p9le": "4:2:0",
                    "yuv420p10be": "4:2:0",
                    "yuv420p10le": "4:2:0",
                    "yuv422p10be": "4:2:2",
                    "yuv422p10le": "4:2:2",
                    "yuv444p9be": "4:4:4",
                    "yuv444p9le": "4:4:4",
                    "yuv444p10be": "4:4:4",
                    "yuv444p10le": "4:4:4",
                    "yuv422p9be": "4:2:2",
                    "yuv422p9le": "4:2:2",
                    "vda_vld": "",
                    "gbrp": "",
                    "gbrp9be": "",
                    "gbrp9le": "",
                    "gbrp10be": "",
                    "gbrp10le": "",
                    "gbrp16be": "",
                    "gbrp16le": "",
                    "yuva420p9be": "4:2:0",
                    "yuva420p9le": "4:2:0",
                    "yuva422p9be": "4:2:2",
                    "yuva422p9le": "4:2:2",
                    "yuva444p9be": "4:4:4",
                    "yuva444p9le": "4:4:4",
                    "yuva420p10be": "4:2:0",
                    "yuva420p10le": "4:2:0",
                    "yuva422p10be": "4:2:2",
                    "yuva422p10le": "4:2:2",
                    "yuva444p10be": "4:4:4",
                    "yuva444p10le": "4:4:4",
                    "yuva420p16be": "4:2:0",
                    "yuva420p16le": "4:2:0",
                    "yuva422p16be": "4:2:2",
                    "yuva422p16le": "4:2:2",
                    "yuva444p16be": "4:4:4",
                    "yuva444p16le": "4:4:4",
                    "vdpau": "",
                    "xyz12le": "",
                    "xyz12be": "",
                    "nv16": "",
                    "nv20le": "",
                    "nv20be": "",
                    "yvyu422": "4:2:2",
                    "vda": "",
                    "ya16be": "",
                    "ya16le": "",
                    "rgba64be": "RGBA",
                    "rgba64le": "RGBA",
                    "bgra64be": "BGRA",
                    "bgra64le": "BGRA",
                    "0rgb": "",
                    "rgb0": "",
                    "0bgr": "",
                    "bgr0": "",
                    "yuva444p": "4:4:4",
                    "yuva422p": "4:2:2",
                    "yuv420p12be": "4:2:0",
                    "yuv420p12le": "4:2:0",
                    "yuv420p14be": "4:2:0",
                    "yuv420p14le": "4:2:0",
                    "yuv422p12be": "4:2:0",
                    "yuv422p12le": "4:2:2",
                    "yuv422p14be": "4:2:2",
                    "yuv422p14le": "4:2:2",
                    "yuv444p12be": "4:4:4",
                    "yuv444p12le": "4:4:4",
                    "yuv444p14be": "4:4:4",
                    "yuv444p14le": "4:4:4",
                    "gbrp12be": "",
                    "gbrp12le": "",
                    "gbrp14be": "",
                    "gbrp14le": "",
                    "gbrap": "",
                    "gbrap16be": "",
                    "gbrap16le": "",
                    "yuvj411p": "4:1:1",
                    "bayer_bggr8": "",
                    "bayer_rggb8": "",
                    "bayer_gbrg8": "",
                    "bayer_grbg8": "",
                    "bayer_bggr16le": "",
                    "bayer_bggr16be": "",
                    "bayer_rggb16le": "",
                    "bayer_rggb16be": "",
                    "bayer_gbrg16le": "",
                    "bayer_gbrg16be": "",
                    "bayer_grbg16le": "",
                    "bayer_grbg16be": ""}

AUDIO_BIT_DEPTHS = {"u8": "8",
                    "s16": "16",
                    "s32": "24",
                    "flt": "",
                    "dbl": "",
                    "u8p": "8",
                    "s16p": "16",
                    "s32p": " 24",
                    "fltp": "",
                    "dblp": ""}

class AVMetadata():
    def __init__(self, fileName):
        self.fileName = fileName
        if self.validateFileType():
            command = GET_XML_COMMAND.split()
            command.append(self.fileName)
            p = Popen(command, stdout=PIPE, stderr=STDOUT, bufsize=0)
            self.rawdata = p.communicate()[0]
            self.fileXML = search('^(<\?xml).*(</ffprobe>)', self.rawdata, DOTALL).group(0)
            self.xmlDom = parseString(self.fileXML)

    def getFormat(self):

        #check if it's an audio format
        for extension in VALID_AUDIO_FILE_EXTENSIONS:
            if extension in self.fileName:
                return "audio"

        #check if it's a video format
        for extension in VALID_VIDEO_FILE_EXTENSIONS:
            if extension in self.fileName:
                return "video"
        return "unknown"

    def sizeof_human(self, num):
        num = int(num)
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def validateFileType(self):
        # check file extensions
        validation = True
        valid_extension = False
        for extension in VALID_VIDEO_FILE_EXTENSIONS:
            if splitext(self.fileName)[1] == extension:
                valid_extension = True
                break
        for extension in VALID_AUDIO_FILE_EXTENSIONS:
            if splitext(self.fileName)[1] == extension:
                valid_extension = True
                break
        if not valid_extension:
            validation = False
        return validation

    def getXML(self):
        return self.fileXML


    def getXMLDom(self):
        return self.xmlDom

    def test(self):
        # for stream in self.xmlDom.getElementsByTagName('stream'):
        pass
            # print stream.getAttribute("codec_type")

    def getTotalRunningTimeRaw(self):
        return search('Duration: ((\d{0,9}):(\d{0,9}):(\d{0,9}).(\d{0,9}))', self.rawdata).group(1)

        pass
    def getVideoTotalFrames(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return int(stream.getAttribute("nb_frames"))
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
                return int(AUDIO_BIT_DEPTHS[stream.getAttribute("sample_fmt")])

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
                return COLORSPACES[stream.getAttribute("pix_fmt")]

    def getVideoColorSampling(self):
        for stream in self.xmlDom.getElementsByTagName('stream'):
            if stream.getAttribute("codec_type") == "video":
                return CHROMA_SUB_SAMPLING[stream.getAttribute("pix_fmt")]

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
        self.sha1 = hashlib.sha1()
        with open(self.fileName,'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                self.sha1.update(chunk)

        return self.sha1.hexdigest()
