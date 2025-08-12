import time
from Messager import Messager
from DictionaryInjector import DictionaryInjector
from nltk.translate.bleu_score import sentence_bleu
import sacrebleu

def calculateBLEU(references, candidates):
    if len(references) != len(candidates):
        raise ValueError("Referanslar ve adaylar aynı uzunlukta olmalıdır.")
    
    bleu_scores = []
    for ref, cand in zip(references, candidates):
        reference = [ref]  # Tek bir referans ise liste içine alınır
        score = sentence_bleu(reference, cand)
        bleu_scores.append(score)
    
    return bleu_scores

api_key = "lm-studio"
url = "http://172.31.160.1:1234/v1"
model = "gemma-3n-e2b-it-text"

models = [
    { "key" : "lm-studio", "url" : "http://127.0.0.1:1234/v1", "model" : "gemma-3n-e2b-it-text" },
    { "key" : "lm-studio", "url" : "http://127.0.0.1:1234/v1", "model" : "qwen/qwen3-8b" },
]

dictionary_file = "Dictionary/Dictionary.json"

#Messager = Messager(api_key, url)
#Messager.SelectModel(model)

DManager = DictionaryInjector()
DManager.SetFile(dictionary_file)

#print(DManager.GetPrompted("Deneme PO ve O2 ile bu ilacı verin."))

testDatas = [
    "Use this drug PO and O2.",
    "The patients PMH includes hypertension and diabetes",
    "She underwent implantation of a DDDR pacemaker last year due to symptomatic bradycardia",
    "The patient was admitted with worsening shortness of breath secondary to CHF.",
    "The records were obtained from an OSH where the patient was initially treated."
]

realDatas = [
    "Bu ilacı ağızdan ve oksijen ile kullan.",
    "Hastanın geçmiş tıbbi öyküsünde hipertansiyon ve diyabet yer almaktadır.",
    "Semptomatik bradikardi nedeniyle geçen yıl DDDR tipi kalp pili takıldı.",
    "Hasta, konjestif kalp yetmezliğine bağlı kötüleşen nefes darlığı ile hastaneye yatırıldı.",
    "Hasta ilk olarak tedavi edildiği dış bir hastaneden kayıtlar temin edildi.",
]

noPromptRes = {
    "gemma-3n-e2b-it-text" : [],
    "qwen/qwen3-8b" : []
}
promptedRes = {
    "gemma-3n-e2b-it-text" : [],
    "qwen/qwen3-8b" : []
}

for model in models:
    messager = Messager(model["key"], model["url"])
    messager.SelectModel(model["model"])
    i = 0
    print("Model = " + str(model))
    
    for testData in testDatas:
        max_retries = 3
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                noprompted = DManager.WithoutPrompt(testData)
                role, message = messager.Message(noprompted)
                noPromptRes[model["model"]].append(message)
                messager.Clear()
                success = True
                i += 1
                if i % 5 == 0:
                    if model["key"] != "lm-studio":
                        print(f"{i}. istekte bekleme yapılıyor...")
                        time.sleep(30)
            except Exception as e:
                messager.Clear()
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Hata oluştu, 30 saniye bekleniyor (Deneme {retry_count}/3)... Hata: {str(e)}")
                    time.sleep(30)
                else:
                    print(f"Son deneme başarısız oldu. Model: {model['model']}, Hata: {str(e)}")

    for testData in testDatas:
        max_retries = 3
        retry_count = 0
        success = False

        while retry_count < max_retries and not success:
            try:
                prompted = DManager.GetPrompted(testData)
                role, message = messager.Message(prompted)
                promptedRes[model["model"]].append(message)
                messager.Clear()
                success = True
                i += 1
                if i % 5 == 0:
                    if model["key"] != "lm-studio":
                        print(f"{i}. istekte bekleme yapılıyor...")
                        time.sleep(30)
            except Exception as e:
                messager.Clear()
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Hata oluştu, 30 saniye bekleniyor (Deneme {retry_count}/3)... Hata: {str(e)}")
                    time.sleep(30)
                else:
                    print(f"Son deneme başarısız oldu. Model: {model['model']}, Hata: {str(e)}")
    
    del messager

print(noPromptRes["gemma-3n-e2b-it-text"])
print("---")
print(promptedRes["gemma-3n-e2b-it-text"])


promptedBLEU = {}
nopromptedBLEU = {}

for model in models:
    modelName = model["model"]
    promptedBLEU[modelName] = []
    nopromptedBLEU[modelName] = []
    
    for test, label in zip(promptedRes[modelName], realDatas):
        bleu = sacrebleu.corpus_bleu([test], [[label]])
        promptedBLEU[modelName].append(bleu.score)
        
    for test, label in zip(noPromptRes[modelName], realDatas):
        bleu = sacrebleu.corpus_bleu([test], [[label]])
        nopromptedBLEU[modelName].append(bleu.score)

prompted_avg = {model: sum(scores) / len(scores) for model, scores in promptedBLEU.items()}
noprompted_avg = {model: sum(scores) / len(scores) for model, scores in nopromptedBLEU.items()}
delta = {model: prompted_avg[model] - noprompted_avg[model] for model in prompted_avg}

print(prompted_avg)
print(noprompted_avg)
print(delta)

max_diff = -float('inf')
min_diff = float('inf')
max_info = ("", -1, 0.0)
min_info = ("", -1, 0.0)

for model in nopromptedBLEU:
    for i in range(len(nopromptedBLEU[model])):
        diff = abs(promptedBLEU[model][i] - nopromptedBLEU[model][i])
        if diff > max_diff:
            max_diff = diff
            max_info = (model, i, diff)
        if diff < min_diff:
            min_diff = diff
            min_info = (model, i, diff)

print(f"Maksimum değişim:\nModel: {max_info[0]}\nİndeks: {max_info[1]}\nFark: {max_info[2]:.4f}")
print("\n")
print(f"Minimum değişim:\nModel: {min_info[0]}\nİndeks: {min_info[1]}\nFark: {min_info[2]:.4f}")