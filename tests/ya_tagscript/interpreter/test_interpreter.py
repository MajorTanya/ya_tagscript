from textwrap import dedent
from unittest.mock import MagicMock

import pytest

from ya_tagscript import (
    TagScriptInterpreter,
    adapters,
    blocks,
    exceptions,
    interfaces,
    interpreter,
)
from ya_tagscript.interpreter.node import Node


@pytest.fixture
def ts_interpreter():
    b = [
        blocks.AssignmentBlock(),
        blocks.CaseBlock(),
        blocks.CommandBlock(),
        blocks.IfBlock(),
        blocks.JoinBlock(),
        blocks.StrictVariableGetterBlock(),
        blocks.MathBlock(),
        blocks.PythonBlock(),
        blocks.ReplaceBlock(),
    ]
    return TagScriptInterpreter(b)


def test_recursion_limit(
    ts_interpreter: TagScriptInterpreter,
):
    script = """{=(recursion):lol}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {=(recursion):{recursion}{recursion}}
    {recursion}""".strip()
    # a formality to make the test correct without having to dedent to the left margin
    script = dedent(script)
    with pytest.raises(
        exceptions.WorkloadExceededError,
        match=r"The Tagscript interpreter has surpassed the workload limit. Processed 2298/2000.",
    ):
        ts_interpreter.process(script, work_limit=2000)


def test_username_sanitation_tag(
    ts_interpreter: TagScriptInterpreter,
):
    script = """\
    {=(ucode1):𝓪 𝓫 𝓬 𝓭 𝓮 𝓯 𝓰 𝓱 𝓲 𝓳 𝓴 𝓵 𝓶 𝓷 𝓸 𝓹 𝓺 𝓻 𝓼 𝓽 𝓾 𝓿 𝔀 𝔁 𝔂 𝔃}
    {=(ucode2):𝕒 𝕓 𝕔 𝕕 𝕖 𝕗 𝕘 𝕙 𝕚 𝕛 𝕜 𝕝 𝕞 𝕟 𝕠 𝕡 𝕢 𝕣 𝕤 𝕥 𝕦 𝕧 𝕨 𝕩 𝕪 𝕫}
    {=(ucode3):ａ ｂ ｃ ｄ ｅ ｆ ｇ ｈ ｉ ｊ ｋ ｌ ｍ ｎ ｏ ｐ ｑ ｒ ｓ ｔ ｕ ｖ ｗ ｘ ｙ ｚ}
    {=(ucode4):ⓐ ⓑ ⓒ ⓓ ⓔ ⓕ ⓖ ⓗ ⓘ ⓙ ⓚ ⓛ ⓜ ⓝ ⓞ ⓟ ⓠ ⓡ ⓢ ⓣ ⓤ ⓥ ⓦ ⓧ ⓨ ⓩ}
    {=(ucode5):🅐 🅑 🅒 🅓 🅔 🅕 🅖 🅗 🅘 🅙 🅚 🅛 🅜 🅝 🅞 🅟 🅠 🅡 🅢 🅣 🅤 🅥 🅦 🅧 🅨 🅩}
    {=(ucode6):𝐚 𝐛 𝐜 𝐝 𝐞 𝐟 𝐠 𝐡 𝐢 𝐣 𝐤 𝐥 𝐦 𝐧 𝐨 𝐩 𝐪 𝐫 𝐬 𝐭 𝐮 𝐯 𝐰 𝐱 𝐲 𝐳}
    {=(ucode7):𝖆 𝖇 𝖈 𝖉 𝖊 𝖋 𝖌 𝖍 𝖎 𝖏 𝖐 𝖑 𝖒 𝖓 𝖔 𝖕 𝖖 𝖗 𝖘 𝖙 𝖚 𝖛 𝖜 𝖝 𝖞 𝖟}
    {=(ucode8):𝒂 𝒃 𝒄 𝒅 𝒆 𝒇 𝒈 𝒉 𝒊 𝒋 𝒌 𝒍 𝒎 𝒏 𝒐 𝒑 𝒒 𝒓 𝒔 𝒕 𝒖 𝒗 𝒘 𝒙 𝒚 𝒛}
    {=(ucode9):𝚊 𝚋 𝚌 𝚍 𝚎 𝚏 𝚐 𝚑 𝚒 𝚓 𝚔 𝚕 𝚖 𝚗 𝚘 𝚙 𝚚 𝚛 𝚜 𝚝 𝚞 𝚟 𝚠 𝚡 𝚢 𝚣}
    {=(ucode10):𝖺 𝖻 𝖼 𝖽 𝖾 𝖿 𝗀 𝗁 𝗂 𝗃 𝗄 𝗅 𝗆 𝗇 𝗈 𝗉 𝗊 𝗋 𝗌 𝗍 𝗎 𝗏 𝗐 𝗑 𝗒 𝗓}
    {=(ucode11):𝗮 𝗯 𝗰 𝗱 𝗲 𝗳 𝗴 𝗵 𝗶 𝗷 𝗸 𝗹 𝗺 𝗻 𝗼 𝗽 𝗾 𝗿 𝘀 𝘁 𝘂 𝘃 𝘄 𝘅 𝘆 𝘇}
    {=(ucode12):𝙖 𝙗 𝙘 𝙙 𝙚 𝙛 𝙜 𝙝 𝙞 𝙟 𝙠 𝙡 𝙢 𝙣 𝙤 𝙥 𝙦 𝙧 𝙨 𝙩 𝙪 𝙫 𝙬 𝙭 𝙮 𝙯}
    {=(ucode13):𝘢 𝘣 𝘤 𝘥 𝘦 𝘧 𝘨 𝘩 𝘪 𝘫 𝘬 𝘭 𝘮 𝘯 𝘰 𝘱 𝘲 𝘳 𝘴 𝘵 𝘶 𝘷 𝘸 𝘹 𝘺 𝘻}
    {=(ucode14):⒜ ⒝ ⒞ ⒟ ⒠ ⒡ ⒢ ⒣ ⒤ ⒥ ⒦ ⒧ ⒨ ⒩ ⒪ ⒫ ⒬ ⒭ ⒮ ⒯ ⒰ ⒱ ⒲ ⒳ ⒴ ⒵}
    {=(ucode15):á b ć d é f ǵ h í j ḱ ĺ ḿ ń ő ṕ q ŕ ś t ú v ẃ x ӳ ź}
    {=(ucode16):ค ๒ ƈ ɗ ﻉ ि ﻭ ɦ ٱ ﻝ ᛕ ɭ ๓ ก ѻ ρ ۹ ɼ ร Շ પ ۷ ฝ ซ ץ չ}
    {=(ucode17):α в ¢ ∂ є ƒ ﻭ н ι נ к ℓ м η σ ρ ۹ я ѕ т υ ν ω χ у չ}
    {=(ucode18):ค ๒ ς ๔ є Ŧ ﻮ ђ เ ן к ɭ ๓ ภ ๏ ק ợ г ร Շ ย ש ฬ א ץ չ}
    {=(ucode19):а ъ с ↁ э f Б Ђ і ј к l м и о р q ѓ ѕ т ц v ш х Ў z}
    {=(ucode20):ል ጌ ር ዕ ቿ ቻ ኗ ዘ ጎ ጋ ጕ ረ ጠ ክ ዐ የ ዒ ዪ ነ ፕ ሁ ሀ ሠ ሸ ሃ ጊ}
    {=(ucode21):𝔞 𝔟 𝔠 𝔡 𝔢 𝔣 𝔤 𝔥 𝔦 𝔧 𝔨 𝔩 𝔪 𝔫 𝔬 𝔭 𝔮 𝔯 𝔰 𝔱 𝔲 𝔳 𝔴 𝔵 𝔶 𝔷}
    {=(ucode22):ä ḅ ċ ḋ ë ḟ ġ ḧ ï j ḳ ḷ ṁ ṅ ö ṗ q ṛ ṡ ẗ ü ṿ ẅ ẍ ÿ ż}
    {=(ucode23):Ⱥ ƀ ȼ đ ɇ f ǥ ħ ɨ ɉ ꝁ ł m n ø ᵽ ꝗ ɍ s ŧ ᵾ v w x ɏ ƶ}
    {=(uppercasesplit):comment variable}
    {=(ucode24):𝓐 𝓑 𝓒 𝓓 𝓔 𝓕 𝓖 𝓗 𝓘 𝓙 𝓚 𝓛 𝓜 𝓝 𝓞 𝓟 𝓠 𝓡 𝓢 𝓣 𝓤 𝓥 𝓦 𝓧 𝓨 𝓩}
    {=(ucode25):𝔸 𝔹 ℂ 𝔻 𝔼 𝔽 𝔾 ℍ 𝕀 𝕁 𝕂 𝕃 𝕄 ℕ 𝕆 ℙ ℚ ℝ 𝕊 𝕋 𝕌 𝕍 𝕎 𝕏 𝕐 ℤ}
    {=(ucode26):Ⓐ Ⓑ Ⓒ Ⓓ Ⓔ Ⓕ Ⓖ Ⓗ Ⓘ Ⓙ Ⓚ Ⓛ Ⓜ Ⓝ Ⓞ Ⓟ Ⓠ Ⓡ Ⓢ Ⓣ Ⓤ Ⓥ Ⓦ Ⓧ Ⓨ Ⓩ}
    {=(ucode27):🅐 🅑 🅒 🅓 🅔 🅕 🅖 🅗 🅘 🅙 🅚 🅛 🅜 🅝 🅞 🅟 🅠 🅡 🅢 🅣 🅤 🅥 🅦 🅧 🅨 🅩}
    {=(ucode28):Ａ Ｂ Ｃ Ｄ Ｅ Ｆ Ｇ Ｈ Ｉ Ｊ Ｋ Ｌ Ｍ Ｎ Ｏ Ｐ Ｑ Ｒ Ｓ Ｔ Ｕ Ｖ Ｗ Ｘ Ｙ Ｚ}
    {=(ucode29):𝐀 𝐁 𝐂 𝐃 𝐄 𝐅 𝐆 𝐇 𝐈 𝐉 𝐊 𝐋 𝐌 𝐍 𝐎 𝐏 𝐐 𝐑 𝐒 𝐓 𝐔 𝐕 𝐖 𝐗 𝐘 𝐙}
    {=(ucode30):𝕬 𝕭 𝕮 𝕯 𝕰 𝕱 𝕲 𝕳 𝕴 𝕵 𝕶 𝕷 𝕸 𝕹 𝕺 𝕻 𝕼 𝕽 𝕾 𝕿 𝖀 𝖁 𝖂 𝖃 𝖄 𝖅}
    {=(ucode31):𝑨 𝑩 𝑪 𝑫 𝑬 𝑭 𝑮 𝑯 𝑰 𝑱 𝑲 𝑳 𝑴 𝑵 𝑶 𝑷 𝑸 𝑹 𝑺 𝑻 𝑼 𝑽 𝑾 𝑿 𝒀 𝒁}
    {=(ucode32):𝖠 𝖡 𝖢 𝖣 𝖤 𝖥 𝖦 𝖧 𝖨 𝖩 𝖪 𝖫 𝖬 𝖭 𝖮 𝖯 𝖰 𝖱 𝖲 𝖳 𝖴 𝖵 𝖶 𝖷 𝖸 𝖹}
    {=(ucode33):𝙰 𝙱 𝙲 𝙳 𝙴 𝙵 𝙶 𝙷 𝙸 𝙹 𝙺 𝙻 𝙼 𝙽 𝙾 𝙿 𝚀 𝚁 𝚂 𝚃 𝚄 𝚅 𝚆 𝚇 𝚈 𝚉}
    {=(ucode34):𝗔 𝗕 𝗖 𝗗 𝗘 𝗙 𝗚 𝗛 𝗜 𝗝 𝗞 𝗟 𝗠 𝗡 𝗢 𝗣 𝗤 𝗥 𝗦 𝗧 𝗨 𝗩 𝗪 𝗫 𝗬 𝗭}
    {=(ucode35):𝘼 𝘽 𝘾 𝘿 𝙀 𝙁 𝙂 𝙃 𝙄 𝙅 𝙆 𝙇 𝙈 𝙉 𝙊 𝙋 𝙌 𝙍 𝙎 𝙏 𝙐 𝙑 𝙒 𝙓 𝙔 𝙕}
    {=(ucode36):𝘈 𝘉 𝘊 𝘋 𝘌 𝘍 𝘎 𝘏 𝘐 𝘑 𝘒 𝘓 𝘔 𝘕 𝘖 𝘗 𝘘 𝘙 𝘚 𝘛 𝘜 𝘝 𝘞 𝘟 𝘠 𝘡}
    {=(ucode37):🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿}
    {=(ucode38):🄰 🄱 🄲 🄳 🄴 🄵 🄶 🄷 🄸 🄹 🄺 🄻 🄼 🄽 🄾 🄿 🅀 🅁 🅂 🅃 🅄 🅅 🅆 🅇 🅈 🅉}
    {=(ucode39):🅰 🅱 🅲 🅳 🅴 🅵 🅶 🅷 🅸 🅹 🅺 🅻 🅼 🅽 🅾 🅿 🆀 🆁 🆂 🆃 🆄 🆅 🆆 🆇 🆈 🆉}
    {=(ucode40):Á B Ć D É F Ǵ H í J Ḱ Ĺ Ḿ Ń Ő Ṕ Q Ŕ ś T Ű V Ẃ X Ӳ Ź}
    {=(ucode41):Д Б Ҁ ↁ Є F Б Н І Ј Ќ L М И Ф Р Q Я Ѕ Г Ц V Щ Ж Ч Z}
    {=(ucode42):𝔄 𝔅 ℭ 𝔇 𝔈 𝔉 𝔊 ℌ ℑ 𝔍 𝔎 𝔏 𝔐 𝔑 𝔒 𝔓 𝔔 ℜ 𝔖 𝔗 𝔘 𝔙 𝔚 𝔛 𝔜 ℨ}
    {=(ucode43):Ä Ḅ Ċ Ḋ Ё Ḟ Ġ Ḧ Ї J Ḳ Ḷ Ṁ Ṅ Ö Ṗ Q Ṛ Ṡ Ṫ Ü Ṿ Ẅ Ẍ Ÿ Ż}
    {=(ucode44):Ⱥ Ƀ Ȼ Đ Ɇ F Ǥ Ħ Ɨ Ɉ Ꝁ Ł M N Ø Ᵽ Ꝗ Ɍ S Ŧ ᵾ V W X Ɏ Ƶ}
    {=(ucode45):ᴀ ʙ ᴄ ᴅ ᴇ ғ ɢ ʜ ɪ ᴊ ᴋ ʟ ᴍ ɴ ᴏ ᴘ ǫ ʀ s ᴛ ᴜ ᴠ ᴡ x ʏ ᴢ}
    {=(ucode):{ucode1} {ucode2} {ucode3} {ucode4} {ucode5} {ucode6} {ucode7} {ucode8} {ucode9} {ucode10} {ucode11} {ucode12} {ucode13} {ucode14} {ucode15} {ucode16} {ucode17} {ucode18} {ucode19} {ucode20} {ucode21} {ucode22} {ucode23} {ucode24} {ucode25} {ucode26} {ucode27} {ucode28} {ucode29} {ucode30} {ucode31} {ucode32} {ucode33} {ucode34} {ucode35} {ucode36} {ucode37} {ucode38} {ucode39} {ucode40} {ucode41} {ucode42} {ucode43} {ucode44} {ucode45}}
    {=(referencemap):a b c d e f g h i j k l m n o p q r s t u v w x y z}
    {=(username):{replace(, ):{target}}}
    {=(username):{if({contains({username(2)}):{ucode}}==true):{replace({username(2)},{{if({m:trunc({index({username(2)}):{ucode}}+1)}>598):upper|lower}:{referencemap({m:trunc(({index({username(2)}):{ucode}}+1)%26)})}}):{username}}|{username}}}
    {=(username):{if({contains({username(3)}):{ucode}}==true):{replace({username(3)},{referencemap({m:trunc(({index({username(3)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(4)}):{ucode}}==true):{replace({username(4)},{referencemap({m:trunc(({index({username(4)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(5)}):{ucode}}==true):{replace({username(5)},{referencemap({m:trunc(({index({username(5)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(6)}):{ucode}}==true):{replace({username(6)},{referencemap({m:trunc(({index({username(6)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(7)}):{ucode}}==true):{replace({username(7)},{referencemap({m:trunc(({index({username(7)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(8)}):{ucode}}==true):{replace({username(8)},{referencemap({m:trunc(({index({username(8)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(9)}):{ucode}}==true):{replace({username(9)},{referencemap({m:trunc(({index({username(9)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(10)}):{ucode}}==true):{replace({username(10)},{referencemap({m:trunc(({index({username(10)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(11)}):{ucode}}==true):{replace({username(11)},{referencemap({m:trunc(({index({username(11)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(12)}):{ucode}}==true):{replace({username(12)},{referencemap({m:trunc(({index({username(12)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(13)}):{ucode}}==true):{replace({username(13)},{referencemap({m:trunc(({index({username(13)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(14)}):{ucode}}==true):{replace({username(14)},{referencemap({m:trunc(({index({username(14)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(15)}):{ucode}}==true):{replace({username(15)},{referencemap({m:trunc(({index({username(15)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(16)}):{ucode}}==true):{replace({username(16)},{referencemap({m:trunc(({index({username(16)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(17)}):{ucode}}==true):{replace({username(17)},{referencemap({m:trunc(({index({username(17)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(18)}):{ucode}}==true):{replace({username(18)},{referencemap({m:trunc(({index({username(18)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(19)}):{ucode}}==true):{replace({username(19)},{referencemap({m:trunc(({index({username(19)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(20)}):{ucode}}==true):{replace({username(20)},{referencemap({m:trunc(({index({username(20)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(21)}):{ucode}}==true):{replace({username(21)},{referencemap({m:trunc(({index({username(21)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(22)}):{ucode}}==true):{replace({username(22)},{referencemap({m:trunc(({index({username(22)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(23)}):{ucode}}==true):{replace({username(23)},{referencemap({m:trunc(({index({username(23)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(24)}):{ucode}}==true):{replace({username(24)},{referencemap({m:trunc(({index({username(24)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(25)}):{ucode}}==true):{replace({username(25)},{referencemap({m:trunc(({index({username(25)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(26)}):{ucode}}==true):{replace({username(26)},{referencemap({m:trunc(({index({username(26)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(27)}):{ucode}}==true):{replace({username(27)},{referencemap({m:trunc(({index({username(27)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(28)}):{ucode}}==true):{replace({username(28)},{referencemap({m:trunc(({index({username(28)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(29)}):{ucode}}==true):{replace({username(29)},{referencemap({m:trunc(({index({username(29)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(30)}):{ucode}}==true):{replace({username(30)},{referencemap({m:trunc(({index({username(30)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(username):{if({contains({username(31)}):{ucode}}==true):{replace({username(31)},{referencemap({m:trunc(({index({username(31)}):{ucode}}+1)%26)})}):{username}}|{username}}}
    {=(error):You can't change your own nickname with Carlbot. Please mention somebody after the tag invocation.}
    {c:{if({target(id)}=={user(id)}):choose {error},{error}|setnick {target(id)} {join():{username}}}}""".strip()
    script = dedent(script)
    username = "𝓑⒜𝐬ٱⓒ U𝘴𝕖𝓻𝔫𝔞мë"
    data = {"target": adapters.StringAdapter(username)}
    response = ts_interpreter.process(script, data)
    assert response.body == ""
    commands = response.actions.get("commands")
    assert commands is not None
    assert commands == [f"setnick {username} BasicUsername"]


def test_single_escaped_brace_is_properly_ignored(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper:\\{up}"
    result = ts_interpreter.process(script).body
    assert result == "\\{UP"


def test_pairs_of_escaped_braces_are_properly_ignored_and_dont_become_blocks(
    ts_interpreter: TagScriptInterpreter,
):
    script = "{upper:\\{my_var\\}}"
    data = {"my_var": adapters.StringAdapter("if you can see this it failed")}
    result = ts_interpreter.process(script, data).body
    assert result == "\\{MY_VAR\\}"


def test_block_rejection_for_text_blocks():
    ts_interpreter = TagScriptInterpreter([])
    mock_ctx = MagicMock(spec=interpreter.Context)
    mock_node = MagicMock(spec=interfaces.NodeABC)
    mock_node.type = Node.text(text_value="test node")

    returned = ts_interpreter._resolve_block_rejection(mock_ctx, mock_node)

    assert returned == ""


def test_glossary_entry_work_limit(
    ts_interpreter: TagScriptInterpreter,
):
    script = """{=(hello):Hello|Hi|Good day|Good morning|Good evening}
    {hello(4):|}
    {hello(5):|}
    {hello(1):|}
    """.strip()
    script = dedent(script)
    with pytest.raises(
        exceptions.WorkloadExceededError,
        match=r"The Tagscript interpreter has surpassed the workload limit. Processed \d{2}/15.",
    ) as e:
        ts_interpreter.process(script, work_limit=15)
    print(e)
