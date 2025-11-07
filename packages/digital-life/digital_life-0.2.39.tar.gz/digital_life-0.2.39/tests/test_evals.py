from pro_craft import AsyncIntel
from digital_life.models import *
import pandas as pd


class Test_Evals:
    def __init__(self,inference_save_case = False,model_name = "doubao-1-5-pro-256k-250115"):
        self.inters = AsyncIntel(model_name = model_name)
        self.inference_save_case = inference_save_case



async def test_memory_card1():
    inters = AsyncIntel(model_name = "doubao-1-5-pro-32k-250115")
    await inters._evals(prompt_id="memorycard-generate-content",OutputFormat = Document,ExtraFormats_list = [Chapter])

    inters.df.to_csv("tests/memory_card.csv",index=False)
    inters.draw_data()

    

"""


    async def evals(self,save_path = None):
        await self.inters._evals(prompt_id="memorycard-score",OutputFormat = MemoryCardScore) # 单一型
        await self.inters._evals(prompt_id="memorycard-merge",OutputFormat = MemoryCard2)
        await self.inters._evals(prompt_id="memorycard-polish",OutputFormat = MemoryCard)
        
        await self.inters._evals(prompt_id="memorycard-format",OutputFormat = MemoryCardGenerate2)
   
        if save_path:
            self.inters.df.to_csv(save_path,index=False)
        
        self.inters.draw_data()
 


    async def evals(self,save_path = None):
        df = pd.DataFrame({"name":[],'status':[],"score":[],"total":[],"bad_case":[]})
        await self.inters._evals(prompt_id="user-overview",OutputFormat = ContentVer, df = df)
        await self.inters._evals(prompt_id="user-relationship-extraction",OutputFormat = CharactersData, df = df)
        await self.inters._evals(prompt_id="avatar-brief",OutputFormat = BriefResponse, df = df)
        # await self.inters._evals(prompt_id="avatar-personality-extraction",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="avatar-desensitization",OutputFormat = BriefResponse, df = df)



        
        if save_path:
            df.to_csv(save_path,index=False)
        
        self.draw_data(df=df)

    async def evals(self,save_path = None):
        df = pd.DataFrame({"name":[],'status':[],"score":[],"total":[],"bad_case":[]})
        await self.inters._evals(prompt_id="biograph_material_init",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph_material_add",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-outline",OutputFormat = "what", df = df)
        await self.inters._evals(prompt_id="biograph-paid-title",OutputFormat = BiographPaidTitle, df = df)
        await self.inters._evals(prompt_id="biograph-brief",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-extract-person-name",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-extract-place",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-extract-material",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-writer",OutputFormat = "", df = df)
        await self.inters._evals(prompt_id="biograph-free-writer",OutputFormat = Biography_Free, df = df)
"""