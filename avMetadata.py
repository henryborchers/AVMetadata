import hashlib
from re import findall, DOTALL,compile, MULTILINE, search
from xml.dom.minidom import parseString

__author__ = 'Henry Borchers'
from subprocess import Popen, PIPE, STDOUT
GET_JSON_COMMAND = 'ffprobe -print_format xml -show_streams'

class AVMetadata():
    def __init__(self, fileName):
        self.fileName = fileName
        command = GET_JSON_COMMAND.split()
        command.append(self.fileName)
        p = Popen(command, stdout=PIPE, stderr=STDOUT, bufsize=0)
        rawData = p.communicate()[0]
        self.fileXML = search('^(<\?xml).*(</ffprobe>)', rawData, DOTALL).group(0)
        self.xmlDom = parseString(self.fileXML)
        print "done"

    def getXML(self):
        return self.fileXML


    def getXMLDom(self):
        return self.xmlDom

    def getJSON(self):

        pass

    def test(self):
        print "test"

    def getTotalRunningTime(self):
        pass

    def getAudioSampleRate(self):
        pass

    def getAudioChannels(self):
        pass

    def getAudioBitDepth(self):
        pass

    def getVideoCodec(self):
        pass

    def getVideoFrameRate(self):
        pass

    def getVideoBitRate(self):
        pass

    def videoBitRateH(self):
        pass

    def videoResolution(self):
        pass

    def videoResolutionHeight(self):
        pass

    def videoResolutionWidth(self):
        pass

    def fileSize(self):
        pass

    def fileSizeH(self):
        pass

    def getMD5(self):
        with open(self.fileName,'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                self.md5 = hashlib.md5(chunk)
        return self.md5.hexdigest()

    def getSHA1(self):
        with open(self.fileName,'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                self.SHA1 = hashlib.sha1(chunk)

        return self.SHA1.hexdigest()
