using System;
using System.Linq;
using System.Collections.Generic;

namespace Kontur.WebPFR
{
	public enum DCType {adv, dsv, dsvReg, zpf, zvuk}
	public class DCInfo
	{
		public DCInfo(IEnumerable<PfrTransaction> txns)
		{
			DcId = txns.First().DcId;
			Upfr = txns.First().UpfrCode;
			Corr = txns.First().CorrectionType;
			Year = txns.First().AccountingYear;
			Time = txns.Last().TransactionTime;
			Type = CalcType(txns);
			Positive = CalcPositive(txns);
			Progress = txns.Max(t => t.Type);
		}

		bool CalcPositive(IEnumerable<PfrTransaction> txns)
		{
			int doc_hash=0, sign_hash=0;
		
			foreach(var txn in txns)
			{
				if(txn.Type == TransactionType.report) 
					doc_hash ^= Hash(txn.Documents);
				if(txn.Type == TransactionType.protocol) 
				{
					doc_hash ^= Hash(txn.Documents);
					sign_hash = Hash(txn.Signatures);
				}
			}
			return (doc_hash == sign_hash);
		}

		DCType CalcType(IEnumerable<PfrTransaction> txns)
		{
			foreach(var txn in txns)
			{
				if(txn.Type == TransactionType.report)
				{
					foreach(var doc in txn.Documents)
					{
						switch(doc.Type)
						{
							case DocumentType.bunch: return DCType.adv;
							case DocumentType.advBunch: return DCType.adv;
							case DocumentType.dsvBunch: return DCType.dsv;
							case DocumentType.dsvRegistry: return DCType.dsvReg;
							case DocumentType.zpfBunch: return DCType.zpf;
							case DocumentType.zvukBunch: return DCType.zvuk;
						}
					}
				}
			}
			return DCType.adv;
		}

		int Hash(IEnumerable<PfrDocument> docs)
		{
			int hash = 0;
			foreach(var doc in docs) hash ^= doc.Id.GetHashCode();
			return hash;
		}

		int Hash(IEnumerable<PfrSignature> signs)
		{
			int hash = 0;
			foreach(var sign in signs) hash ^= sign.DocId.GetHashCode();
			return hash;
		}

		public string Upfr;
		public Guid DcId;
		public DateTime Time;
		public CorrectionType Corr;
		public int Year;
		public DCType Type;
		public TransactionType Progress {get; private set;}
		public bool Positive {get; private set;}
	}
}
