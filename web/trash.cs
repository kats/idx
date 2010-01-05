using System;

namespace Kontur.WebPFR
{
	public static class fn
	{
		public static string TypeToString(DCType t)
		{
			switch(t)
			{
				case DCType.adv: return "Годовая отчетность"; 
				case DCType.dsv: return "Заявление о вступлении в систему добровольного страхования";
				case DCType.dsvReg: return "Реестр лиц, за которых перечислены дополнительные страховые взносы";
				case DCType.zpf: return "Заявление о переходе в НПФ";
				case DCType.zvuk: return "Заявление о выборе управляющей компании";
				default: return "";
			}
		}

		public static string CorrYearString(DCType t, CorrectionType c, int y)
		{
			return string.Format("{0}за {1} год", 
				t == DCType.adv ?
					c == CorrectionType.Abrogative ? "отменяющие " : 
					c == CorrectionType.Corrective ? "корректирующие " : ""
					: "", y);
		}
	}
}
