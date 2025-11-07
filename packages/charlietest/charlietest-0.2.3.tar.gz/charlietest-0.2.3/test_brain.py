from charlietest.example import chat_completion

if __name__ == "__main__":
    API_key = "2B-Lc1dTjbiQd23FpRWhh6X48mzOyhaxcTTTUR5mK46uhcPOLBKFa"
    content = """"What is the capital of France?"""
    print(chat_completion(API_key,content))