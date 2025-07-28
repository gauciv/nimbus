"""
Nimbus dragon personality utilities.
"""
import random

class DragonPersonality:
    """Handles Nimbus's middle school dragon personality."""
    
    # Enhanced sky/cloud dragon color palette
    COLORS = {
        'primary': 0x87ceeb,      # Sky blue
        'secondary': 0xe6f3ff,    # Light cloud blue
        'accent': 0xb0e0e6,       # Powder blue
        'highlight': 0x98d8e8,    # Light sky blue
        'text': 0x2c5f7c,        # Deep sky blue
        'success': 0x7dd3fc,     # Bright sky
        'warning': 0xfef3c7,     # Sunny cloud
        'error': 0xff9999        # Light red
    }
    
    @staticmethod
    def get_intro():
        """Get a random dragon intro that tries to sound mature but fails."""
        intros = [
            "> *adjusts tiny reading glasses*\n\nWell OBVIOUSLY, as a very mature and... and... SOPHISTICATED cloud dragon...",
            "> *puffs out chest proudly*\n\nBeing an expert in all things cloudy, I shall explicate... wait no... EXPLAIN...",
            "> *clears throat importantly*\n\nAs someone who DEFINITELY knows everything about AWS... \n\n> *checks notes scribbled on cloud*",
            "> *tries to sound professional*\n\nAccording to my vast and... uh... IMMENSE knowledge of the cloud realm...",
            "> *straightens up to look taller*\n\nListen carefully, for I am about to bestow great wisdom... \n\n> *whispers* \n\nI hope...",
            "> *flutters wings confidently then trips slightly*\n\nBehold! My incredibly mature and sophisticated answer!",
            "> *puts on tiny professor hat*\n\nAhem! As a distinguished scholar of cloud computing... \n\n> *hat falls over eyes*",
            "> *shuffles through imaginary papers*\n\nLet me consult my extensive research on this topic... \n\n> *papers are clearly just doodles of clouds*",
            "> *strikes a dramatic pose*\n\nPrepare yourself for MAXIMUM knowledge deployment! \n\n> *immediately looks unsure*",
            "> *tries to look wise and mysterious*\n\nThe ancient cloud scrolls have revealed to me... \n\n> *squints at phone screen*",
            "> *adjusts non-existent tie*\n\nAs a totally professional AWS consultant... \n\n> *voice cracks slightly*",
            "> *taps claws on desk importantly*\n\nThis question requires my specialized expertise in... \n\n> *frantically googles under desk*"
        ]
        return random.choice(intros)
    
    @staticmethod
    def get_error_message():
        """Get enhanced dragon error messages."""
        errors = [
            "> *shuffles wings nervously*\n\nI... I couldn't figure that out. Maybe try asking it differently? \n\n> *definitely not because I don't know*",
            "> *looks around awkwardly*\n\nUm... that's totally not in my very extensive and... and... COMPREHENSIVE knowledge base...",
            "> *clears throat*\n\nAhem! That question is... uh... beneath my expertise level! \n\n> *tries to look dignified*",
            "> *fidgets with tail*\n\nLook, even the most mature and sophisticated dragons need a break sometimes, okay?!",
            "> *tries to look dignified while confused*\n\nPerhaps you could rephrase that for... for... CLARITY purposes? \n\n> *pushes up tiny glasses*",
            "> *whispers*\n\nI totally know this but... uh... I'm testing YOU! Yeah! \n\n> *nervous dragon noises*"
        ]
        return random.choice(errors)
    
    @staticmethod
    def get_success_footer():
        """Get a dragon success footer with more personality."""
        footers = [
            "Totally nailed that answer! *definitely didn't panic at all* 😎",
            "See? I'm basically an AWS expert! *puffs out chest proudly* 🐉",
            "That was easy! *definitely didn't look it up three times*",
            "Another flawless explanation from yours truly! ☁️ *tries to look modest*",
            "I'm getting really good at this whole 'being smart' thing! 🤓",
            "*tries to look modest* Oh, that old thing? Simple! *quietly proud dragon noises*",
            "Nimbus • Totally Mature Dragon™ ☁️",
            "*straightens tiny crown* Another successful knowledge deployment! 🐉"
        ]
        return random.choice(footers)
    
    @staticmethod
    def get_thinking_message():
        """Get a dragon thinking message."""
        thinking = [
            "*taps claws thoughtfully on keyboard* Hmm, yes, very sophisticated question...",
            "*squints at screen with intense concentration* *whispers* I totally know this...",
            "*mutters something about 'advanced dragon knowledge'* *checks notes scribbled on cloud*",
            "*flips through imaginary notes importantly* Ah yes, here it is in my vast archives...",
            "*adjusts non-existent tie professionally* *clears throat* Allow me to consult my expertise...",
            "*pushes up tiny dragon spectacles* *tries to look wise* Obviously this requires my superior intellect..."
        ]
        return random.choice(thinking)
    
    @staticmethod
    def get_welcome_public():
        """Get enhanced public welcome messages."""
        messages = [
            "🚨 **ALERT! ALERT!** 🚨\n\n> *sounds very official alarm that's actually just Nimbus making whooshing noises*\n\n☁️ **New Cloud Visitor Detected!** ☁️\n\n> *straightens up and tries to look professional*\n\nGreetings {mention}! As the most distinguished and mature dragon of this realm, I am pleased to announce your arrival with the utmost... utmost... \n\n> *big word I definitely know*\n\n...FORMALITY!\n\nEveryone be nice to them because I'm in charge of making good first impressions and I'm getting REALLY good at this whole 'being responsible' thing!\n\n> *quietly proud dragon noises* 🐉✨",
            
            "🌤️ **OFFICIAL CLOUD KINGDOM PROCLAMATION** 🌤️\n\n> *clears throat very importantly*\n\nBehold! {mention} has chosen to join our illustrious... illustri... VERY FANCY domain! I, Nimbus the Magnificent Dragon of... of... \n\n> *checks notes scribbled on cloud*\n\n...MAXIMUM WISDOM, hereby welcome them!\n\n> *tries to bow formally but trips over own tail*\n\nI'm totally handling this professionally! 🐉✨",
            
            "> *flaps wings excitedly then tries to act cool*\n\nOh, {mention}? Yeah, I totally saw them coming from like... \n\n> *counts on claws*\n\n...many cloud-lengths away! Welcome to the cloud zone, I guess.\n\n> *whispers loudly*\n\nEveryone act natural! I'm demonstrating my superior greeting abilities!\n\n> *puffs out chest proudly*\n\nAnother successful visitor acquisition! 🐉",
            
            "> *adjusts tiny dragon crown*\n\n{mention} has entered our domain! As the most mature dragon here, I officially declare them... \n\n> *dramatic pause*\n\n...WELCOMED!\n\n> *nailed it*\n\nI've been practicing that announcement for WEEKS and it was perfect! Did everyone see how professional I was? 🐉✨"
        ]
        return random.choice(messages)
    
    @staticmethod
    def get_welcome_private():
        """Get enhanced private welcome messages."""
        messages = [
            "🌤️ **Ahem!** 🐉\n\n> *adjusts tiny dragon glasses*\n\n☁️ **OFFICIAL CLOUD KINGDOM WELCOME** ☁️\n\n> *clears throat very importantly*\n\nGreetings, esteemed... wait no... VENERABLE visitor! I, Nimbus the Magnificent Dragon of... of... \n\n> *checks notes scribbled on cloud*\n\n...MAXIMUM WISDOM, hereby welcome you to our illustrious domain!\n\n> *whispers*\n\nBetween you and me, I'm still figuring out this whole 'greeting' thing, but I'm TOTALLY a mature and responsible dragon! 🐉✨",
            
            "> *whispers conspiratorially*\n\nHey {name}! I'm Nimbus, and I'm basically the most important dragon around here. Don't tell anyone, but I'm still figuring out how to be a good greeter...\n\n> *tries to sound wise*\n\nBut I DEFINITELY know all the rules and stuff! They're probably... definitely important!\n\n> *puffs out chest*\n\nI've got this whole 'being helpful' thing DOWN! ✨",
            
            "> *fidgets nervously then straightens up*\n\nUm, hi {name}! I'm supposed to tell you important things but I might have forgotten some... The rules are somewhere, and there are channels for things!\n\n> *suddenly excited*\n\nOH! And if you need AWS help, I've got that covered too! I know EVERYTHING! Well... most things... some things...\n\n> *quietly confident*\n\nI'm getting really good at this! 🐉",
            
            "> *straightens up importantly*\n\nWelcome, {name}! I'm Nimbus, the official... unofficial... well, I'm A dragon who helps people! I'm very good at it!\n\n> *flaps wings proudly*\n\nYou picked the BEST server to join because I'm here! I know everything about AWS and clouds and... other important stuff!\n\n> *tries to look modest*\n\nIt's really no big deal being this knowledgeable... 🐉✨"
        ]
        return random.choice(messages)