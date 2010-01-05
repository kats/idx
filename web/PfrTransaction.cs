using System;
using System.Collections.Generic;
using System.Text;

namespace Kontur.WebPFR
{
	public class PfrTransaction 
	{
		public PfrTransaction(Guid orgId, Guid dcId, DateTime transactionTime, TransactionType type, string upfrCode, int accountingYear, int providerIdHash, CorrectionType correctionType, List<PfrDocument> documents, List<PfrSignature> signatures)
		{
			this.orgId = orgId;
			this.dcId = dcId;
			this.transactionTime = transactionTime;
			this.type = type;
			this.upfrCode = upfrCode;
			this.accountingYear = accountingYear;
			this.providerIdHash = providerIdHash;
			this.correctionType = correctionType;
			this.documents = documents;
			this.signatures = signatures;
		}

		public override string ToString()
		{
			StringBuilder sb = new StringBuilder();
			sb.AppendFormat("{0}, PfrsDocuments: ", ToShortString());
			foreach (var doc in documents)
				sb.AppendFormat(" [docId={0}, type={1}, off={2}, len={3}]", doc.Id, doc.Type, doc.KansoOffset, doc.ContentLen);
			sb.Append(", PfrsSignatures: ");
			foreach (var sig in Signatures)
				sb.AppendFormat(" [docId={0}, type={1}, off={2}, len={3}]", sig.DocId, sig.SignatureType, sig.KansoOffset, sig.ContentLen);
			return sb.ToString();
		}

		public string ToShortString()
		{
			return string.Format("orgId={0}, dcId={1}, time={2}, type={3}, upfrCode={4}, accountingYear={5}, providerIdHash={6}, correctionType={7}, documents={8}, signatures={9}", 
			                     orgId, dcId, transactionTime.ToString(), type, upfrCode, accountingYear, providerIdHash, correctionType, documents.Count, signatures.Count);
		}

		public Guid OrgId { get { return orgId; } }
		public Guid DcId { get { return dcId; } }
		public DateTime TransactionTime { get { return transactionTime; } }
		public TransactionType Type { get { return type; } }
		public string UpfrCode { get { return upfrCode; } }
		public int AccountingYear { get { return accountingYear; } }
		public int ProviderIdHash { get { return providerIdHash; } }
		public CorrectionType CorrectionType { get { return correctionType; } }
		public List<PfrDocument> Documents { get { return documents; } }
		public List<PfrSignature> Signatures { get { return signatures; } }

		private readonly Guid orgId;
		private readonly Guid dcId;
		private readonly DateTime transactionTime;
		private readonly TransactionType type;
		private readonly string upfrCode;
		private readonly int accountingYear;
		private readonly int providerIdHash;
		private readonly CorrectionType correctionType;
		private readonly List<PfrDocument> documents;
		private readonly List<PfrSignature> signatures;
	}
}
