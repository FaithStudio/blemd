#! /usr/bin/python3
from .BinaryReader import BinaryReader
from .BinaryWriter import BinaryWriter
from .pseudobones import getBoneByName
import mathutils
import bpy
import logging
log = logging.getLogger('bpy.ops.import_mesh.bmd.bck')
from math import nan, pi, isnan, isclose, ceil


class BckKey:
    # <variable time>
    # -- float 
    # <variable value>
    # -- float 
    # <variable tangent>
    # -- float  //??
    def __init__(self, tm=0, vl=0.0, tg=0.0):  # GENERATED!
        self.time = tm
        self.value = vl
        self.tangent = tg

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return (self.time == other.time and
                isclose(self.value, other.value, rel_tol=1E-3) and
                isclose(self.tangent, other.tangent, rel_tol=1E-3))


class BckJointAnim:
    # <variable scalesX>
    # -- std::vector<Key>
    # <variable scalesY>
    # -- std::vector<Key>
    # <variable scalesZ>
    # -- std::vector<Key>
    # <variable rotationsX>
    # -- std::vector<Key>
    # <variable rotationsY>
    # -- std::vector<Key>
    # <variable rotationsZ>
    # -- std::vector<Key>
    # <variable translationsX>
    # -- std::vector<Key>
    # <variable translationsY>
    # -- std::vector<Key>
    # <variable translationsZ>
    # -- std::vector<Key>
    def __init__(self):  # GENERATED!
        self.scalesX = []
        self.rotationsY = []
        self.rotationsZ = []
        self.scalesZ = []
        self.translationsZ = []
        self.translationsX = []
        self.rotationsX = []
        self.translationsY = []
        self.scalesY = []
        self.frames_scale = set()
        self.frames_rotation = set()
        self.frames_translation = set()
    # ------------------------------------

    def __eq__(self, other):
        return (self.scalesX == other.scalesX and
                self.scalesY == other.scalesY and
                self.scalesZ == other.scalesZ and
                self.rotationsX == other.rotationsX and
                self.rotationsY == other.rotationsY and
                self.rotationsZ == other.rotationsZ and
                self.translationsX == other.translationsX and
                self.translationsY == other.translationsY and
                self.translationsZ == other.translationsZ)


class BckAnk1Header:
    """# <variable tag>
    # -- char[4] 'ANK1'
    # <variable sizeOfSection>
    # -- u32 
    # -- 0 - play once, 2 - loop
    # <variable loopFlags>
    # -- u8 
    # <variable angleMultiplier>
    # -- u8 all angles have to multiplied by pow(2, angleMultiplyer)
    # <variable animationLength>
    # -- u16 in time units
    # <variable numJoints>
    # -- u16 that many animated joints at offsetToJoints
    # <variable scaleCount>
    # --u16  that many floats at offsetToScales
    # <variable rotCount>
    # -- u16 that many s16s at offsetToRots
    # <variable transCount>
    # -- u16 that many floats at offsetToTrans
    # <variable offsetToJoints>
    # -- u32 
    # <variable offsetToScales>
    # -- u32 
    # <variable offsetToRots>
    # -- u32 
    # <variable offsetToTrans>
    # -- u32 
    # <function>"""

    def __init__(self):  # GENERATED!
        pass

    def LoadData(self, br):
                
      self.tag = br.ReadFixedLengthString(4)
      self.sizeOfSection = br.ReadDWORD()
      self.loopFlags = br.GetByte()
      self.angleMultiplier = br.GetByte()
      self.animationLength = br.ReadWORD()
      self.numJoints = br.ReadWORD()
      self.scaleCount = br.ReadWORD()
      self.rotCount = br.ReadWORD()
      self.transCount = br.ReadWORD()
      self.offsetToJoints = br.ReadDWORD()
      self.offsetToScales = br.ReadDWORD()
      self.offsetToRots = br.ReadDWORD()
      self.offsetToTrans = br.ReadDWORD()
    # -- TODO: the following two structs have really silly names, rename them

    def DumpData(self, bw):
        bw.writeString(self.tag)
        bw.writeDword(self.sizeOfSection)
        bw.writeByte(self.loopFlags)
        bw.writeByte(self.angleMultiplier)
        bw.writeWord(self.animationLength)
        bw.writeWord(self.numJoints)
        bw.writeWord(self.scaleCount)
        bw.writeWord(self.rotCount)
        bw.writeWord(self.transCount)
        bw.writeDword(self.offsetToJoints)
        bw.writeDword(self.offsetToScales)
        bw.writeDword(self.offsetToRots)
        bw.writeDword(self.offsetToTrans)


class BckAnimIndex:
    # <variable count>
    # -- u16 
    # <variable index>
    # -- u16 
    # <variable zero>
    # -- u16 always 0?? -> no (biawatermill01.bck) TODO: find out what it means
    # <function>

    def __init__(self):  # GENERATED!
        pass

    def LoadData(self, br):
        self.count = br.GetSHORT()
        self.index = br.GetSHORT()
        self.zero = br.GetSHORT()

    def DumpData(self, bw):
        bw.writeShort(self.count)
        bw.writeShort(self.index)
        bw.writeShort(self.zero)


class BckAnimComponent:
    # <variable s>
    # -- AnimIndex scale
    # <variable r>
    # -- AnimIndex rotation
    # <variable t>
    # -- AnimIndex translation
    # <function>

    def __init__(self):  # GENERATED!
        self.s= BckAnimIndex()
        self.r= BckAnimIndex()
        self.t= BckAnimIndex()

    def LoadData(self, br):
     self.s.LoadData(br)
     self.r.LoadData(br)
     self.t.LoadData(br)

    def DumpData(self, bw):
     self.s.DumpData(bw)
     self.r.DumpData(bw)
     self.t.DumpData(bw)
  

class BckAnimatedJoint:
    # --if count > 1, count*3 floats/shorts stored at index (time, value, unk [interpolation info, e.g. tangent??])?
    # --for shorts, time is a "real" short, no fixedpoint
    # <variable x>
    # -- AnimComponent 
    # <variable y>
    # -- AnimComponent 
    # <variable z>
    # -- AnimComponent 
    # <function>

    def __init__(self):  # GENERATED!
        self.z= BckAnimComponent()
        self.y= BckAnimComponent()
        self.x= BckAnimComponent()

    def LoadData(self, br):
     self.x.LoadData(br)
     self.y.LoadData(br)
     self.z.LoadData(br)

    def DumpData(self, bw):
     self.x.DumpData(bw)
     self.y.DumpData(bw)
     self.z.DumpData(bw)


# -----------------------------------------------


class Bck_in:
    """# <variable anims>
    # -- std::vector<JointAnim>
    # <variable animationLength>
    # -- int
    # <variable currAnimTime>
    # -- float
    # -- ConvRotation(vector<Key>& rots, float scale)
    # <function>

    # -- void readComp(vector<Key>& dst, const vector<T>& src, const bck::AnimIndex& index)
    # <function>

    # <function>

    # <function>

    # <function>

    # <function>

    # -- the caller has to ensure that jnt1.frames and bck.anims contain
    # --the same number of elements
    # <function>

    # -- IMPORTANT: scale values are absolute and not related to the parent
    # -- e.g Bone A (scale=200%), Bone B (Scale=200%), Bone C (Scale=100%). Bone A is the parent of Bone B and Bone B is the parent of Bone C
    # --  need to remove the parent scaling. e.g Bone C shouldn't change in size but in 3DS max it will equal 400% (2 * 2 * 1 * 100)
    # <function>

    # -- CalcScale anims[i].scalesX parentBoneIndexs 8
    # <function>

    # -- only calc on first parent. ignore boneIndex
    # <function>

    # -- gets total x scale (excluding self)
    # -- bck file stores the absolute scale at that point and should ignore all parent bone scaling
    # -- e.g. bone a (200%) -> bone b (200%) -> bone C (200%).
    # -- bone a (1 * 2 * 100), bone b ((1 / 2 (bone a scale)) * 2 * 100 = 50 %), bone c (1/2 * 1/2 * 100 = 25%)
    # -- however, the parent bone is already scaled based on all items before it so only the parents scale is required. e.g. bone c (1/2 * 100 = 50) because bone b is already at 50%, total scale = 50%*50%=25%
    # -- WARNING: skewed bones?
    # <function>

    # <function>

    # <function>

    # <function>

    # <function>

    # -- could use timeOffset to load all animations one after another
    # -- parentBoneIndexs array of ints. e.g. parentBoneIndexs[2] = 1 (2nd bones parent is the first bone)
    # <function>

    # -- deltaTime in ticks
    # <function>

    # -- from stdplugs/stdscripts/CharacterPluginObject.ms
    # <function>

    # -- from stdplugs/stdscripts/CharacterPluginObject.ms
    # <function>

    # <function>"""

    def __init__(self):  # GENERATED!
        self.anims = []

    def ConvRotation(self, rots, scale):
        for rot in rots:
            rot.value *= scale
            rot.tangent *= scale
        return rots

    def ReadComp(self, src, index):
        dst = []
        # -- dst.resize(index.count);

        # -- violated by biawatermill01.bck

        if index.zero != 0:
            log.warning("readComp(): index `zero` variable is non-zero. This animation might look broken")
        if index.count <= 0:
            log.warning("readComp(): count is <= 0")
        elif index.count == 1:
            dst.append(None)
            dst[0] = BckKey()  # fixed 4 lines
            dst[0].time = 0
            dst[0].value = src[index.index]
            dst[0].tangent = 0
        else:
            for j in range(index.count):  # (int j = 0; j < index.count; ++j)
                while len(dst) <= j:
                    dst.append(None)
                dst[j] = BckKey()
                dst[j].time = src[(index.index + 3*j)]
                dst[j].value = src[(index.index + 3*j + 1)]
                dst[j].tangent = src[(index.index + 3*j + 2)]
        return dst

    def LoadAnk1(self, br, jointnum):
        i = 0
        ank1Offset = br.Position()

        # -- read header
        h = BckAnk1Header()
        h.LoadData(br)

        if h.numJoints != jointnum:
            return  # this file will not be used anyway

        self.currAnimTime = 0.0
        self.animationLength = h.animationLength

        # -- read scale floats:
        br.SeekSet(ank1Offset + h.offsetToScales)
        scales = [br.GetFloat() for _ in range(h.scaleCount)]

        # -- read rotation s16s:
        br.SeekSet(ank1Offset + h.offsetToRots)
        rotations = [br.GetSHORT() for _ in range(h.rotCount)]

        # -- read translation floats:
        br.SeekSet(ank1Offset + h.offsetToTrans)
        translations = [br.GetFloat() for _ in range(h.transCount)]

        # -- read joints
        rotScale = (pow(2., h.angleMultiplier) * pi / 32768.)  # result in RADIANS  per increment (in a short)
        br.SeekSet(ank1Offset + h.offsetToJoints)
        self.anims = []
        # -- bck.self.anims.resize(h.numJoints);

        for i in range(h.numJoints):
            joint = BckAnimatedJoint()
            joint.LoadData(br)
            while len(self.anims) <= i:
                self.anims.append(None)
            self.anims[i] = BckJointAnim()
            self.anims[i].scalesX = self.ReadComp(scales, joint.x.s)
            self.anims[i].scalesY = self.ReadComp(scales, joint.y.s)
            self.anims[i].scalesZ = self.ReadComp(scales, joint.z.s)

            self.anims[i].rotationsX = self.ReadComp(rotations, joint.x.r)
            self.anims[i].rotationsZ = self.ReadComp(rotations, joint.z.r)
            self.anims[i].rotationsY = self.ReadComp(rotations, joint.y.r)
            self.anims[i].rotationsX = self.ConvRotation(self.anims[i].rotationsX, rotScale)
            self.anims[i].rotationsY = self.ConvRotation(self.anims[i].rotationsY, rotScale)
            self.anims[i].rotationsZ = self.ConvRotation(self.anims[i].rotationsZ, rotScale)

            self.anims[i].translationsX = self.ReadComp(translations, joint.x.t)
            self.anims[i].translationsY = self.ReadComp(translations, joint.y.t)
            self.anims[i].translationsZ = self.ReadComp(translations, joint.z.t)

    def LoadBck(self, filePath, jointlen):
        br = BinaryReader()
        br.Open(filePath)  #, compressed_stream=True)
        # optimise, since it will likely not be completely read
        br.SeekSet(0x20)
        size = 0
        i = 0
        while i < 1:
            br.SeekCur(size)
            pos = br.Position()
            tag = br.ReadFixedLengthString(4)
            size = br.ReadDWORD()

            if size < 8:
                size = 8  # -- prevent endless loop on corrupt data

            br.SeekSet(pos)

            if tag == "ANK1":
                self.LoadAnk1(br, jointlen)
            else:
                # MessageBox("readBck(): Unsupported section " + tag)
                raise ValueError("readBck(): Unsupported section " + tag)
            br.SeekSet(pos)
            i += 1
        br.Close()

    # no use here
    def Interpolate(self, v1, d1, v2, d2, t):  # -- t in [0,1]
        # linear imterpolation:
        # return v1+t*(v1-v1)

        # --cubic interpolation:
        # -- float values
        a = 2*(v1 - v2) + d1 + d2
        b = -3 * v1 + 3 * v2 - 2 * d1 - d2
        c = d1
        d = v1
        # --TODO: yoshi_walk.bck has strange-looking legs...not sure if
        # --the following line is to blame, though
        return ((a*t + b)*t + c) *t + d

    # TODO: erase dummy bone system
    def GetPositionBone(self, curBone):
        dummyBone = getBoneByName(curBone.name.fget() + "_dummy")

        if dummyBone is None:
            return curBone

        else:
            return dummyBone

    # function which only has docs in it. Whut?!
    def ValidateScale(self, curBone, scaleValue):

        """# --if (scaleValue != 1 and curBone.children.count > 1) then
        # --	throw (curBone.name + " unable to scale ( " +(scaleValue as string)+" ) bones with more than one child bone")"""

    # GOT it!
    def AnimateBoneFrames(self, timeOffset, bones, frameScale, includeScaling):
        # --alert (bones.count as string)

        for i in range(len(bones)):
            bone = bones[i]
            anim = self.anims[i]

            bone.frames.feed_anim(anim, includeScaling, frameScale, timeOffset)
            pass
            # # position correction LATER in the program
            # if includeScaling:
            #     translate_animation(timeOffset, bone, anim, frameScale,
            #               'scale', 'x', mathutils.Vector((nan, nan, nan)))
            #     translate_animation(timeOffset, bone, anim, frameScale,
            #               'scale', 'y', mathutils.Vector((nan, nan, nan)))
            #     translate_animation(timeOffset, bone, anim, frameScale,
            #               'scale', 'z', mathutils.Vector((nan, nan, nan)))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'rotation', 'x', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'rotation', 'y', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'rotation', 'z', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'position', 'x', mathutils.Vector((nan, nan, nan)))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'position', 'y', mathutils.Vector((nan, nan, nan)))
            # translate_animation(timeOffset, bone, anim, frameScale,
            #           'position', 'z', mathutils.Vector((nan, nan, nan)))
            #
            # if includeScaling:
            #     complete_animation(timeOffset, bone, anim, self.animationLength,
            #                         'scale', 'x', mathutils.Vector((nan, nan, nan)))
            #     complete_animation(timeOffset, bone, anim, self.animationLength,
            #                         'scale', 'y', mathutils.Vector((nan, nan, nan)))
            #     complete_animation(timeOffset, bone, anim, self.animationLength,
            #                         'scale', 'z', mathutils.Vector((nan, nan, nan)))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'rotation', 'x', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'rotation', 'y', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'rotation', 'z', mathutils.Euler((nan, nan, nan), 'XYZ'))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'position', 'x', mathutils.Vector((nan, nan, nan)))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'position', 'y', mathutils.Vector((nan, nan, nan)))
            # complete_animation(timeOffset, bone, anim, self.animationLength,
            #                     'position', 'z', mathutils.Vector((nan, nan, nan)))


class Bck_out:

    def __init__(self):
        self.maxframe=0

    def calcmultiplier(self, anims):
        ret = 1  # number of total full turns

    def dump_data(self, dst, src):
        index = BckAnimIndex()
        index.zero = 0
        index.count = len(src)
        if len(src) == 1:
            if src[0].time or src[0].tangent:  # if non-zero
                raise ValueError("static animation should be static")
            if src[0].value in dst:
                index.index = dst.index(src[0].value)
            else:
                dst.append(src[0].value)
                index.index = len(dst)-1

        else:
            index.index = len(dst)
            for com in src:
                dst.append(com.time)
                self.maxframe = max(self.maxframe, com.time)
                dst.append(com.value)
                dst.append(com.tangent)

        return index

    def calibrate_rotation(self, rots, scale):
        for j in range(len(rots)):  #
            rots[j].value = round(rots[j].value / scale)
            rots[j].tangent = round(rots[j].tangent / scale)

    def dump_ank1(self, anims, bw):

        Ank1Offset = bw.Position()
        h = BckAnk1Header()
        h.angleMultiplier = 1  # self.calcmultiplier(anims)
        rot_scale = (pow(2., h.angleMultiplier) * pi / 32768.)

        positions = []
        rotations = []
        scales = []
        joints = []


        for anim in anims:
            joint = BckAnimatedJoint()
            joints.append(joint)
            joint.x = BckAnimComponent()
            joint.y = BckAnimComponent()
            joint.z = BckAnimComponent()

            joint.x.s = self.dump_data(scales, anim.scalesX)
            joint.y.s = self.dump_data(scales, anim.scalesY)
            joint.z.s = self.dump_data(scales, anim.scalesZ)

            joint.x.t = self.dump_data(positions, anim.translationsX)
            joint.y.t = self.dump_data(positions, anim.translationsY)
            joint.z.t = self.dump_data(positions, anim.translationsZ)

            self.calibrate_rotation(anim.rotationsX, rot_scale)
            self.calibrate_rotation(anim.rotationsY, rot_scale)
            self.calibrate_rotation(anim.rotationsZ, rot_scale)
            joint.x.r = self.dump_data(rotations, anim.rotationsX)
            joint.y.r = self.dump_data(rotations, anim.rotationsY)
            joint.z.r = self.dump_data(rotations, anim.rotationsZ)

        h.numJoints = len(joints)
        h.scaleCount = len(scales)
        h.rotCount = len(rotations)
        h.transCount = len(positions)
        h.offsetToJoints = 64
        h.offsetToScales = ceil(h.numJoints*3*3*3*2/16)*16 + h.offsetToJoints
        h.offsetToRots = ceil(h.scaleCount*4/16)*16 + h.offsetToScales
        h.offsetToTrans = ceil(h.rotCount*2/16)*16 + h.offsetToRots
        h.animationLength = self.maxframe
        h.tag = 'ANK1'
        h.sizeOfSection = h.offsetToTrans + ceil(h.transCount*4/16)*16 +16
        h.loopFlags = 0  # 0: once, 2: loop

        h.DumpData(bw)
        bw.writePadding(h.offsetToJoints+Ank1Offset - bw.Position())
        for joint in joints:
            joint.DumpData(bw)
        bw.writePadding(h.offsetToScales+Ank1Offset - bw.Position())
        for val in scales:
            bw.WriteFloat(val)
        bw.writePadding(h.offsetToRots+Ank1Offset - bw.Position())
        for val in rotations:
            bw.writeShort(val)
        bw.writePadding(h.offsetToTrans+Ank1Offset - bw.Position())
        for val in positions:
            bw.WriteFloat(val)
        bw.writePadding(h.sizeOfSection+ Ank1Offset - bw.Position())

    def dump_bck(self, anims, filePath):
        bw = BinaryWriter()
        bw.Open(filePath)
        #bw.SeekSet(0x20)
        for _ in range(32):
            bw.writeByte(0x00)
        self.dump_ank1(anims, bw)
        bw.Close()


def create_static_animation(frames):
    anims=[]
    for fr in frames:
        anim = BckJointAnim()
        anims.append(anim)
        anim.scalesX.append(BckKey())
        anim.scalesY.append(BckKey())
        anim.scalesZ.append(BckKey())
        anim.rotationsX.append(BckKey())
        anim.rotationsY.append(BckKey())
        anim.rotationsZ.append(BckKey())
        anim.translationsX.append(BckKey())
        anim.translationsY.append(BckKey())
        anim.translationsZ.append(BckKey())

        anim.scalesX[0].value = fr.sx
        anim.scalesY[0].value = fr.sy
        anim.scalesZ[0].value = fr.sz
        anim.rotationsX[0].value = fr.rx
        anim.rotationsY[0].value = fr.ry
        anim.rotationsZ[0].value = fr.rz
        anim.translationsX[0].value = fr.t.x
        anim.translationsY[0].value = fr.t.y  # dont reflip translation values
        anim.translationsZ[0].value = fr.t.z
    return anims
