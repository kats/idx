using System;

namespace Kontur.WebPFR
{
	public enum DCStatus {Sent, Acc_Sign, Rej_Sign, Acc_Fin, Rej_Fin, Received, Error}
	public enum DCType {adv, dsv, dsvReg, zpf, zvuk}
	public class DCInfo
	{
		public DCInfo(DCStatus status, string upfr, DCType type, Guid dcId, DateTime time, CorrectionType corr, int year) 
		{
			Status=status; Upfr=upfr; Type=type; DcId=dcId; Time=time; Corr=corr; Year=year;
		}

		public string Upfr;
		public Guid DcId;
		public DateTime Time;
		public CorrectionType Corr;
		public int Year;
		public DCStatus Status;
		public DCType Type;
	}

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
