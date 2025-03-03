
from Algorithms.utils import *
from Env_JSP_FJSP.I_Job_Shop import I_Job_shop
from log import SingletonLogger
logger = SingletonLogger.get_logger()

class I_popi:
    def __init__(self,args,CHS,fitness,J_site,len1,r):
        self.args=args
        self.fitness = fitness
        self.J_site=J_site
        self.l1=len1
        self.IJS=I_Job_shop(args,J_site)
        self.r = r+1
        if self.args.means_m>1:
            self.decode(CHS)
            self.CHS,self.fitness,self.SOF = self.NeighborhoodAdjustment(CHS)
            self.CHS,self.fitness,self.SOF = self.FAS_LSR(self.CHS, self.IJS.C_max_job, self.IJS.C_max2_job, self.IJS.C_max3_job)


    def decode(self,CHS):
        logger.info(f"CHS:{CHS}")
        for i in range(self.l1):
            O_num=self.IJS.Jobs[CHS[i]].cur_op
            m_idx=self.J_site.index((CHS[i],O_num))
            logger.info(f"i:{i},O_num:{O_num},m_idx:{m_idx}")
            logger.info(f"CHS[i]:{CHS[i]},CHS[m_idx + self.l1]:{CHS[m_idx + self.l1]},CHS[m_idx + self.l1 * 2]:{CHS[m_idx + self.l1 * 2]}")
            self.IJS.decode(CHS[i], CHS[m_idx + self.l1], CHS[m_idx + self.l1 * 2])
        energy = self.IJS.enenrgy()
        return self.IJS.C_max,energy

    def NeighborhoodAdjustment(self, CHS):
        longest_paths_m = self.IJS.MachineCriticalPath()
        longest_paths_w = self.IJS.LSRCriticalPath()
        if self.r == 1:
            logger.info(f"operator 1,CHS:{CHS}")
            '''
            operator 1
            '''
            End = True
            for i in range(len(longest_paths_m)):
                num_mj = 0
                while End:
                    temp_CHS,num_mj,End = self.IJS.ChangeMachineForOp(CHS, longest_paths_m[i], num_mj)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness,0 
        elif self.r == 2:
            logger.info(f"operator 2,CHS:{CHS}")
            '''
            operator 2
            '''
            End = True
            for i in range(len(longest_paths_m)):
                num_b = 0 ; num_j = 0
                while End:
                    temp_CHS,num_b,num_j,End = self.IJS.SwapROps(CHS, longest_paths_m[i], num_b, num_j)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness, 0 
        elif self.r == 3:
            logger.info(f"operator 3,CHS:{CHS}")
            '''
            operator 3
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS,type,End = self.IJS.RSwapOps(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 4:
            logger.info(f"operator 4,CHS:{CHS}")
            '''
            operator 4
            '''
            End = True
            for i in range(len(longest_paths_w)):
                num_wj = 0
                while End:
                    temp_CHS,num_wj,End = self.IJS.OpSwapLSR(CHS, longest_paths_w[i], num_wj)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    num_wj+=1
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness, 0
        elif self.r == 5:
            logger.info(f"operator 5,CHS:{CHS}")
            '''
            operator 5
            '''
            End = True
            for i in range(len(longest_paths_w)):
                num_b = 0 ; num_w = 0
                while End:
                    temp_CHS,num_b,num_w,End = self.IJS.SwapTwoLSRsAndOps(CHS, longest_paths_w[i], num_b, num_w)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness, 0 
        elif self.r == 6:
            logger.info(f"operator 6,CHS:{CHS}")
            '''
            operator 6
            '''
            End = True
            for i in range(len(longest_paths_m)):
                num_mj = 0
                while End:
                    temp_CHS,num_mj,End = self.IJS.OpAndLSR(CHS, longest_paths_m[i], num_mj)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness,0  
        elif self.r == 7:
            logger.info(f"operator 7,CHS:{CHS}")
            '''
            operator 7
            '''
            End = True
            for i in range(len(longest_paths_m)):
                num_b = 0
                num_j = 0
                while End:
                    temp_CHS, num_b, num_j, End = self.IJS.LSRsAndOps(CHS, longest_paths_m[i], num_b, num_j)  
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness, self.fitness):
                        return temp_CHS, temp_fitness, 1
                    self.IJS.reset() 
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 8:
            logger.info(f"operator 8,CHS:{CHS}")
            '''
            operator 8
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS,type,End = self.IJS.SwapOpsAndLSR(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness,self.fitness):
                        return temp_CHS,temp_fitness,1
                    self.IJS.reset()
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 9:
            logger.info(f"operator 9,CHS:{CHS}")
            '''
            operator 9
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS, type, End = self.IJS.SwapLSRAndOpsP(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness, self.fitness):
                        return temp_CHS, temp_fitness, 1
                    self.IJS.reset() 
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 10:
            logger.info(f"operator 10,CHS:{CHS}")
            '''
            operator 10
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS, type, End = self.IJS.SwapLSRAndOpsPP(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness, self.fitness):
                        return temp_CHS, temp_fitness, 1
                    self.IJS.reset() 
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 11:
            logger.info(f"operator 11,CHS:{CHS}")
            '''
            operator 11
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS, type, End = self.IJS.LSRsAndOpsSwap(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness, self.fitness):
                        return temp_CHS, temp_fitness, 1
                    self.IJS.reset() 
                    self.decode(CHS)
            return CHS, self.fitness, 0  
        elif self.r == 12:
            logger.info(f"operator 12,CHS:{CHS}")
            '''
            operator 12
            '''
            End = True
            for i in range(len(longest_paths_m)):
                type = 0
                while End:
                    logger.info(f"type:{type}")
                    temp_CHS, type, End = self.IJS.LSRsAndOpsSwapP(CHS, longest_paths_m[i], type)
                    self.IJS.reset()
                    temp_fitness = list(self.decode(temp_CHS))
                    if list_Fenjie(temp_fitness, self.fitness):
                        return temp_CHS, temp_fitness, 1
                    self.IJS.reset() 
                    self.decode(CHS)
            return CHS, self.fitness, 0  

    def FAS_LSR(self, CHS, C_max_job, C_max2_job, C_max3_job):
        cidx_C_max_list,cidx_C_max2_list,cidx_C_max3_list = self.IJS.FindLSRLoca(CHS, C_max_job, C_max2_job, C_max3_job)
        for max_idx,max in enumerate(cidx_C_max_list):
            temp_CHS = self.IJS.ChangeOpsSequence(CHS, max_idx, max)
            self.IJS.reset()
            temp_fitness = list(self.decode(temp_CHS))
            if list_Fenjie(temp_fitness, self.fitness):
                return temp_CHS, temp_fitness, 1
            self.IJS.reset() 
            self.decode(CHS)
        for max_idx,max in enumerate(cidx_C_max2_list):
            temp_CHS = self.IJS.ChangeOpsSequence(CHS, max_idx, max)
            self.IJS.reset()
            temp_fitness = list(self.decode(temp_CHS))
            if list_Fenjie(temp_fitness, self.fitness):
                return temp_CHS, temp_fitness, 1
            self.IJS.reset() 
            self.decode(CHS)
        for max_idx,max in enumerate(cidx_C_max3_list):
            temp_CHS = self.IJS.ChangeOpsSequence(CHS, max_idx, max)
            self.IJS.reset()
            temp_fitness = list(self.decode(temp_CHS))
            if list_Fenjie(temp_fitness, self.fitness):
                return temp_CHS, temp_fitness, 1
            self.IJS.reset() 
            self.decode(CHS)
        return CHS, self.fitness, 0  