import os 
from pymongo import MongoClient
from dotenv import load_dotenv

# IMPORTANT: Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/") 
client = MongoClient(MONGO_URI) 
db = client["citizen_portal"] 
services_col = db["services"] 

# Clear existing services
services_col.delete_many({})
print("🗑️  Cleared existing services")

# Complete set of 20 ministries with proper translations
docs = [ 
    { 
        "id":"ministry_it", 
        "name":{
            "en":"Ministry of IT & Digital Affairs",
            "si":"තොරතුරු තාක්ෂණ අමාත්‍යංශය",
            "ta":"தகவல் தொழில்நுட்ப அமைச்சு"
        }, 
        "subservices":[ 
            {
                "id":"it_cert",
                "name":{
                    "en":"IT Certificates",
                    "si":"අයිටී සහතික",
                    "ta":"ஐடி சான்றிதழ்கள்"
                }, 
                "questions":[ 
                    {
                        "q":{
                            "en":"How to apply for an IT certificate?",
                            "si":"IT සහතිකය සඳහා ඉල්ලීම් කරන ආකාරය?",
                            "ta":"ஐடி சான்றிதழுக்கு விண்ணப்பிப்பது எப்படி?"
                        }, 
                        "answer":{
                            "en":"Fill online form and upload NIC.",
                            "si":"ඔන්ලයින් ෆෝරමය පුරවා NIC උඩුගත කරන්න.",
                            "ta":"ஆன்லைனில் படிவத்தை நிரப்பி NIC ஐ பதிவேற்று."
                        }, 
                        "downloads":["/static/forms/it_cert_form.pdf"], 
                        "location":"https://maps.google.com/?q=Ministry+of+IT", 
                        "instructions":"Visit the digital portal, register and submit application."
                    } 
                ] 
            } 
        ] 
    }, 
    {
        "id":"ministry_education",
        "name":{
            "en":"Ministry of Education",
            "si":"අධ්‍යාපන අමාත්‍යංශය",
            "ta":"கல்வி அமைச்சு"
        }, 
        "subservices":[ 
            {
                "id":"schools",
                "name":{
                    "en":"Schools",
                    "si":"පාසල්",
                    "ta":"பள்ளிகள்"
                }, 
                "questions":[ 
                    {
                        "q":{
                            "en":"How to register a school?",
                            "si":"පාසලක් ලියාපදිංචි කිරීම?",
                            "ta":"பள்ளியை பதிவு செய்வது எப்படி?"
                        }, 
                        "answer":{
                            "en":"Complete registration form and submit documents.",
                            "si":"ලියාපදිංචි ෆෝරමය පුරවා ලේඛන ඉදිරිපත් කරන්න.",
                            "ta":"பதிவு படிவத்தை பூர்த்தி செய்து ஆவணங்களை சமர்ப்பிக்கவும்."
                        }, 
                        "downloads":["/static/forms/school_reg.pdf"], 
                        "location":"https://maps.google.com/?q=Ministry+of+Education", 
                        "instructions":"Follow the guidelines on the education portal."
                    } 
                ] 
            }, 
            {
                "id":"exams",
                "name":{
                    "en":"Exams & Results",
                    "si":"විභාග සහ ප්‍රතිඵල",
                    "ta":"பரீட்சைகள் மற்றும் முடிவுகள்"
                }, 
                "questions":[ 
                    {
                        "q":{
                            "en":"How to apply for national exam?",
                            "si":"ජාතික විභාගයට අයදුම් කරන ආකාරය?",
                            "ta":"தேசிய தேர்விற்கு எப்படி விண்ணப்பிப்பது?"
                        }, 
                        "answer":{
                            "en":"Register via examination portal.",
                            "si":"විභාග පෝර්ටල් හරහා ලියාපදිංචි වන්න.",
                            "ta":"பரீட்சை போர்ட்டலின் மூலம் பதிவு செய்யவும்."
                        }, 
                        "downloads":[], 
                        "location":"", 
                        "instructions":"Check exam schedule and fee."
                    } 
                ] 
            } 
        ] 
    },
    {
        "id":"ministry_health",
        "name":{
            "en":"Ministry of Health",
            "si":"සෞඛ්‍ය අමාත්‍යංශය",
            "ta":"சுகாதார அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"General Health Services",
                    "si":"සාමාන්‍ය සෞඛ්‍ය සේවා",
                    "ta":"பொது சுகாதார சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"What health services are available?",
                            "si":"ලබා ගත හැකි සෞඛ්‍ය සේවා මොනවාද?",
                            "ta":"கிடைக்கும் சுகாதார சேவைகள் என்ன?"
                        },
                        "answer":{
                            "en":"Check the health services portal for available services.",
                            "si":"ලබා ගත හැකි සේවා සඳහා සෞඛ්‍ය සේවා පෝර්ටලය පරීක්ෂා කරන්න.",
                            "ta":"கிடைக்கும் சேவைகளுக்கு சுகாதார சேவைகள் போர்ட்டலைப் பார்க்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Visit nearest health center for more information."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_transport",
        "name":{
            "en":"Ministry of Transport",
            "si":"ප්‍රවාහන අමාත්‍යංශය",
            "ta":"போக்குவரத்து அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Transport Services",
                    "si":"ප්‍රවාහන සේවා",
                    "ta":"போக்குவரத்து சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to apply for driving license?",
                            "si":"රියදුරු බලපත්‍රයට අයදුම් කරන්නේ කෙසේද?",
                            "ta":"ஓட்டுநர் உரிமத்திற்கு எவ்வாறு விண்ணப்பிப்பது?"
                        },
                        "answer":{
                            "en":"Visit the DMV office with required documents.",
                            "si":"අවශ්‍ය ලේඛන සමග DMV කාර්යාලයට පිවිසෙන්න.",
                            "ta":"தேவையான ஆவணங்களுடன் DMV அலுவலகத்தை பார்வையிடவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Bring NIC and medical certificate."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_imm",
        "name":{
            "en":"Ministry of Immigration",
            "si":"ආගමන හා විගමන අමාත්‍යංශය",
            "ta":"குடிவரவு அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Immigration Services",
                    "si":"ආගමන සේවා",
                    "ta":"குடிவரவு சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to renew passport?",
                            "si":"විදේශ ගමන් බලපත්‍රය අළුත් කරන්නේ කෙසේද?",
                            "ta":"கடவுச்சீட்டை எவ்வாறு புதுப்பிப்பது?"
                        },
                        "answer":{
                            "en":"Visit immigration with current passport and NIC.",
                            "si":"වත්මන් විදේශ ගමන් බලපත්‍රය සහ ජාතික හැඳුනුම්පත සමඟ ආගමන දෙපාර්තමේන්තුවට යන්න.",
                            "ta":"தற்போதைய கடவுச்சீட்டு மற்றும் NIC உடன் குடிவரவு நிலையத்திற்குச் செல்லவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Processing time: 2-3 weeks."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_foreign",
        "name":{
            "en":"Ministry of Foreign Affairs",
            "si":"විදේශ කටයුතු අමාත්‍යංශය",
            "ta":"வெளிநாட்டு விவகார அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Consular Services",
                    "si":"කොන්සියුලර් සේවා",
                    "ta":"தூதரக சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to get document attestation?",
                            "si":"ලේඛන සත්‍යාපනය ලබා ගන්නේ කෙසේද?",
                            "ta":"ஆவண சான்றிதழ் எவ்வாறு பெறுவது?"
                        },
                        "answer":{
                            "en":"Submit documents to foreign ministry for attestation.",
                            "si":"සත්‍යාපනය සඳහා ලේඛන විදේශ අමාත්‍යාංශයට ඉදිරිපත් කරන්න.",
                            "ta":"சான்றிதழுக்காக ஆவணங்களை வெளியுறவு அமைச்சகத்தில் சமர்ப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Check service fees on official website."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_finance",
        "name":{
            "en":"Ministry of Finance",
            "si":"මුදල් අමාත්‍යංශය",
            "ta":"நிதி அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Financial Services",
                    "si":"මූල්‍ය සේවා",
                    "ta":"நிதி சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to file tax returns?",
                            "si":"බදු ප්‍රකාශන ගොනු කරන්නේ කෙසේද?",
                            "ta":"வரி அறிக்கைகளை எவ்வாறு தாக்கல் செய்வது?"
                        },
                        "answer":{
                            "en":"Use online tax portal to file returns.",
                            "si":"ප්‍රකාශන ගොනු කිරීමට ඔන්ලයින් බදු පෝර්ටලය භාවිතා කරන්න.",
                            "ta":"வருமானத்தை தாக்கல் செய்ய ஆன்லைன் வரி நுழைவாயிலைப் பயன்படுத்தவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Register on IRD portal."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_labour",
        "name":{
            "en":"Ministry of Labour",
            "si":"කම්කරු අමාත්‍යංශය",
            "ta":"தொழிலாளர் அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Employment Services",
                    "si":"රැකියා සේවා",
                    "ta":"வேலைவாய்ப்பு சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to register for job seeking?",
                            "si":"රැකියා සෙවීම සඳහා ලියාපදිංචි වන්නේ කෙසේද?",
                            "ta":"வேலைத்தேடலுக்கு எவ்வாறு பதிவு செய்வது?"
                        },
                        "answer":{
                            "en":"Register on national job portal.",
                            "si":"ජාතික රැකියා පෝර්ටලයේ ලියාපදිංචි වන්න.",
                            "ta":"தேசிய வேலை வாய்ப்பு நுழைவாயிலில் பதிவு செய்யவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Bring updated CV and certificates."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_public",
        "name":{
            "en":"Ministry of Public Administration",
            "si":"රාජ්‍ය පරිපාලන අමාත්‍යංශය",
            "ta":"பொது நிர்வாக அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Public Services",
                    "si":"රාජ්‍ය සේවා",
                    "ta":"பொது சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to apply for government jobs?",
                            "si":"රජයේ රැකියා සඳහා අයදුම් කරන්නේ කෙසේද?",
                            "ta":"அரசு வேலைகளுக்கு எவ்வாறு விண்ணப்பிப்பது?"
                        },
                        "answer":{
                            "en":"Check government job portal for vacancies.",
                            "si":"පුරප්පාඩු සඳහා රජයේ රැකියා පෝර්ටලය පරීක්ෂා කරන්න.",
                            "ta":"காலியிடங்களுக்கு அரசாங்க வேலை வாய்ப்பு போர்ட்டலைச் சரிபார்க்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Follow application guidelines."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_justice",
        "name":{
            "en":"Ministry of Justice",
            "si":"යුක්තිය අමාත්‍යංශය",
            "ta":"நீதி அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Legal Services",
                    "si":"නීති සේවා",
                    "ta":"சட்ட சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to get legal aid?",
                            "si":"නීති ආධාර ලබා ගන්නේ කෙසේද?",
                            "ta":"சட்ட உதவி எவ்வாறு பெறுவது?"
                        },
                        "answer":{
                            "en":"Apply through legal aid commission.",
                            "si":"නීති ආධාර කොමිෂන් සභාව හරහා අයදුම් කරන්න.",
                            "ta":"சட்ட உதவி ஆணையம் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Provide income proof and case details."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_housing",
        "name":{
            "en":"Ministry of Housing",
            "si":"නිවාස අමාත්‍යංශය",
            "ta":"வீட்டு வசதி அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Housing Services",
                    "si":"නිවාස සේවා",
                    "ta":"வீட்டு சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to apply for housing scheme?",
                            "si":"නිවාස යෝජනා ක්‍රමයට අයදුම් කරන්නේ කෙසේද?",
                            "ta":"வீட்டுத் திட்டத்திற்கு எவ்வாறு விண்ணப்பிப்பது?"
                        },
                        "answer":{
                            "en":"Submit application through housing portal.",
                            "si":"නිවාස පෝර්ටලය හරහා අයදුම්පත ඉදිරිපත් කරන්න.",
                            "ta":"வீட்டு நுழைவாயில் மூலம் விண்ணப்பத்தை சமர்ப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Check eligibility criteria first."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_agri",
        "name":{
            "en":"Ministry of Agriculture",
            "si":"කෘෂිකර්ම අමාත්‍යංශය",
            "ta":"விவசாய அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Agricultural Services",
                    "si":"කෘෂිකාර්මික සේවා",
                    "ta":"விவசாய சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to get farming subsidies?",
                            "si":"ගොවිතැන් සහනාධාර ලබා ගන්නේ කෙසේද?",
                            "ta":"விவசாய மானியங்களைப் பெறுவது எப்படி?"
                        },
                        "answer":{
                            "en":"Apply through agrarian services office.",
                            "si":"ගොවිජන සේවා කාර්යාලය හරහා අයදුම් කරන්න.",
                            "ta":"விவசாய சேவைகள் அலுவலகம் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Bring land ownership documents."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_youth",
        "name":{
            "en":"Ministry of Youth Affairs",
            "si":"තරුණ කටයුතු අමාත්‍යංශය",
            "ta":"இளைஞர் விவகார அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Youth Services",
                    "si":"තරුණ සේවා",
                    "ta":"இளைஞர் சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"What youth programs are available?",
                            "si":"ලබා ගත හැකි තරුණ වැඩසටහන් මොනවාද?",
                            "ta":"கிடைக்கும் இளைஞர் திட்டங்கள் என்ன?"
                        },
                        "answer":{
                            "en":"Check youth services portal for programs.",
                            "si":"වැඩසටහන් සඳහා තරුණ සේවා පෝර්ටලය පරීක්ෂා කරන්න.",
                            "ta":"திட்டங்களுக்கு இளைஞர் சேவைகள் போர்ட்டலைப் பார்க்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Age limit: 18-35 years."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_defence",
        "name":{
            "en":"Ministry of Defence",
            "si":"ආරක්ෂක අමාත්‍යංශය",
            "ta":"பாதுகாப்பு அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Defence Services",
                    "si":"ආරක්ෂක සේවා",
                    "ta":"பாதுகாப்பு சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to join armed forces?",
                            "si":"ත්‍රිවිධ හමුදාවට බැඳෙන්නේ කෙසේද?",
                            "ta":"ஆயுதப்படைகளில் எவ்வாறு சேருவது?"
                        },
                        "answer":{
                            "en":"Apply through official recruitment portal.",
                            "si":"නිල බඳවා ගැනීම් පෝර්ටලය හරහා අයදුම් කරන්න.",
                            "ta":"அதிகாரப்பூர்வ ஆட்சேர்ப்பு போர்ட்டல் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Must meet physical and educational requirements."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_tourism",
        "name":{
            "en":"Ministry of Tourism",
            "si":"සංචාරක අමාත්‍යංශය",
            "ta":"சுற்றுலா அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Tourism Services",
                    "si":"සංචාරක සේවා",
                    "ta":"சுற்றுலா சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to register tourism business?",
                            "si":"සංචාරක ව්‍යාපාරයක් ලියාපදිංචි කරන්නේ කෙසේද?",
                            "ta":"சுற்றுலா வணிகத்தை எவ்வாறு பதிவு செய்வது?"
                        },
                        "answer":{
                            "en":"Apply through tourism development authority.",
                            "si":"සංචාරක සංවර්ධන අධිකාරිය හරහා අයදුම් කරන්න.",
                            "ta":"சுற்றுலா மேம்பாட்டு ஆணையம் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Business license and tax registration required."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_trade",
        "name":{
            "en":"Ministry of Industry & Trade",
            "si":"කර්මාන්ත හා වෙළඳ අමාත්‍යංශය",
            "ta":"தொழில் மற்றும் வர்த்தக அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Trade Services",
                    "si":"වෙළඳ සේවා",
                    "ta":"வர்த்தக சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to register a business?",
                            "si":"ව්‍යාපාරයක් ලියාපදිංචි කරන්නේ කෙසේද?",
                            "ta":"வணிகத்தை எவ்வாறு பதிவு செய்வது?"
                        },
                        "answer":{
                            "en":"Register through business registration portal.",
                            "si":"ව්‍යාපාර ලියාපදිංචි පෝර්ටලය හරහා ලියාපදිංචි වන්න.",
                            "ta":"வணிக பதிவு நுழைவாயில் மூலம் பதிவு செய்யவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Provide business plan and capital proof."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_energy",
        "name":{
            "en":"Ministry of Power & Energy",
            "si":"බලශක්ති අමාත්‍යංශය",
            "ta":"மின்சாரம் மற்றும் எரிசக்தி அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Energy Services",
                    "si":"බලශක්ති සේවා",
                    "ta":"எரிசக்தி சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to apply for new electricity connection?",
                            "si":"නව විදුලි සම්බන්ධතාවයක් සඳහා අයදුම් කරන්නේ කෙසේද?",
                            "ta":"புதிய மின்சார இணைப்புக்கு எவ்வாறு விண்ணப்பிப்பது?"
                        },
                        "answer":{
                            "en":"Apply through electricity board online portal.",
                            "si":"විදුලිබල මණ්ඩල ඔන්ලයින් පෝර්ටලය හරහා අයදුම් කරන්න.",
                            "ta":"மின்சார வாரிய ஆன்லைன் நுழைவாயில் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Provide property ownership documents."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_water",
        "name":{
            "en":"Ministry of Water Supply",
            "si":"ජල සම්පාදන අමාත්‍යංශය",
            "ta":"நீர் வழங்கல் அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Water Services",
                    "si":"ජල සේවා",
                    "ta":"நீர் சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to get new water connection?",
                            "si":"නව ජල සම්බන්ධතාවයක් ලබා ගන්නේ කෙසේද?",
                            "ta":"புதிய நீர் இணைப்பு எவ்வாறு பெறுவது?"
                        },
                        "answer":{
                            "en":"Apply through water board portal.",
                            "si":"ජල මණ්ඩල පෝර්ටලය හරහා අයදුම් කරන්න.",
                            "ta":"நீர் வாரிய நுழைவாயில் மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Connection fee applicable."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_env",
        "name":{
            "en":"Ministry of Environment",
            "si":"පරිසර අමාත්‍යංශය",
            "ta":"சுற்றுச்சூழல் அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Environmental Services",
                    "si":"පාරිසරික සේවා",
                    "ta":"சுற்றுச்சூழல் சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to get environmental clearance?",
                            "si":"පාරිසරික අනුමැතිය ලබා ගන්නේ කෙසේද?",
                            "ta":"சுற்றுச்சூழல் அனுமதி எவ்வாறு பெறுவது?"
                        },
                        "answer":{
                            "en":"Submit project proposal to environmental authority.",
                            "si":"ව්‍යාපෘති යෝජනාව පරිසර අධිකාරියට ඉදිරිපත් කරන්න.",
                            "ta":"திட்ட முன்மொழிவை சுற்றுச்சூழல் ஆணையத்திற்கு சமர்ப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"EIA report required for major projects."
                    }
                ]
            }
        ]
    },
    {
        "id":"ministry_culture",
        "name":{
            "en":"Ministry of Culture",
            "si":"සංස්කෘතික අමාත්‍යංශය",
            "ta":"கலாச்சார அமைச்சு"
        },
        "subservices":[
            {
                "id":"general",
                "name":{
                    "en":"Cultural Services",
                    "si":"සංස්කෘතික සේවා",
                    "ta":"கலாச்சார சேவைகள்"
                },
                "questions":[
                    {
                        "q":{
                            "en":"How to register cultural organization?",
                            "si":"සංස්කෘතික සංවිධානයක් ලියාපදිංචි කරන්නේ කෙසේද?",
                            "ta":"கலாச்சார அமைப்பை எவ்வாறு பதிவு செய்வது?"
                        },
                        "answer":{
                            "en":"Apply through cultural affairs department.",
                            "si":"සංස්කෘතික කටයුතු දෙපාර්තමේන්තුව හරහා අයදුම් කරන්න.",
                            "ta":"கலாச்சார விவகார துறை மூலம் விண்ணப்பிக்கவும்."
                        },
                        "downloads":[],
                        "location":"",
                        "instructions":"Provide organization details and objectives."
                    }
                ]
            }
        ]
    }
]

# Insert all services
result = services_col.insert_many(docs)
total = services_col.count_documents({})

print(f"✅ Successfully seeded {len(result.inserted_ids)} services!")
print(f"📊 Total services in database: {total}")

# Show sample
print("\n📋 Sample services:")
for service in services_col.find().limit(5):
    print(f"   - {service['id']}: {service['name']['en']} | {service['name']['si']} | {service['name']['ta']}")

print("\n🎉 Database seeding complete!")
print("Next step: Run 'python app.py' to start the application")