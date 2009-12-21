using System;
using System.IO;
using System.Text;
using Kontur.Utilities;

namespace Kontur.WebPFR
{
	internal class PfrTransactionSerializer
	{
		public void Serialize(Stream output, PfrTransaction pfrTransaction)
		{
			CheckConditionsOfApplicability(output);
			long beginOffset = output.Position;
			ObjectSerializer serializer = new ObjectSerializer(output);
			serializer.Write(LABEL, Encoding.ASCII);
			serializer.Write(pfrTransaction.OrgId);
			serializer.Write(pfrTransaction.DcId);
			serializer.Write(pfrTransaction.TransactionTime);
			serializer.Write((int)pfrTransaction.Type);
			serializer.WriteStringWithLen(pfrTransaction.UpfrCode, Encoding.UTF8);
			serializer.Write(pfrTransaction.AccountingYear);
			serializer.Write(pfrTransaction.ProviderIdHash);
			serializer.Write((int)pfrTransaction.CorrectionType);
			SerializeDocuments(serializer, pfrTransaction);
			SerializeSignatures(serializer, pfrTransaction);
			//hash shamanism
			output.Position = beginOffset;
			int hash = HashCalculator.Calc(output);
			serializer.Write(hash);
		}

		private void SerializeSignatures(ObjectSerializer serializer, PfrTransaction pfrTransaction)
		{
			serializer.Write(pfrTransaction.Signatures.Count);
			foreach(var sig in pfrTransaction.Signatures)
			{
				serializer.Write(sig.Id);
				serializer.Write(sig.DocId);	
				serializer.Write((int)sig.SignatureType);	
				serializer.Write(sig.KansoOffset);	
				serializer.Write(sig.ContentLen);	
			}
		}

		private void SerializeDocuments(ObjectSerializer serializer, PfrTransaction pfrTransaction)
		{
			serializer.Write(pfrTransaction.Documents.Count);
			foreach(var doc in pfrTransaction.Documents)
			{
				serializer.Write(doc.Id);
				serializer.Write((int)doc.Type);
				serializer.Write(doc.FormKey);
				serializer.WriteStringWithLen(doc.FileName, Encoding.UTF8);
				serializer.Write(doc.KansoOffset);
				serializer.Write(doc.ContentLen);
			}
		}

		private void CheckConditionsOfApplicability(Stream stream)
		{
			if (!stream.CanSeek) throw new ArgumentException("Output stream must support Seek()");
			if (!stream.CanRead) throw new ArgumentException("Output stream must support Read()");
			if (!stream.CanWrite) throw new ArgumentException("Output stream must support Write()");
		}

		public const string LABEL = "====";
	}
}