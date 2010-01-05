using System;

namespace Kontur.WebPFR
{
	public class PfrSignature
	{
		public PfrSignature(Guid id, Guid docId, SignatureType signatureType, long kansoOffset, int contentLen)
		{
			this.id = id;
			this.docId = docId;
			this.signatureType = signatureType;
			this.contentLen = contentLen;
			this.kansoOffset = kansoOffset;
		}

		public override string ToString()
		{
			return string.Format("id = {0}, docId = {1}, type = {2}, len = {3}, off = {4}", id, docId, signatureType, contentLen, kansoOffset);
		}

		public bool Equals(PfrSignature other)
		{
			if(ReferenceEquals(null, other)) return false;
			if(ReferenceEquals(this, other)) return true;
			return other.id.Equals(id) && other.docId.Equals(docId) && Equals(other.signatureType, signatureType) && other.contentLen == contentLen && other.kansoOffset == kansoOffset;
		}

		public override bool Equals(object obj)
		{
			if(ReferenceEquals(null, obj)) return false;
			if(ReferenceEquals(this, obj)) return true;
			if(obj.GetType() != typeof(PfrSignature)) return false;
			return Equals((PfrSignature)obj);
		}

		public override int GetHashCode()
		{
			unchecked
			{
				int result = id.GetHashCode();
				result = (result * 397) ^ docId.GetHashCode();
				result = (result * 397) ^ signatureType.GetHashCode();
				result = (result * 397) ^ contentLen;
				result = (result * 397) ^ kansoOffset.GetHashCode();
				return result;
			}
		}

		public static bool operator ==(PfrSignature left, PfrSignature right) { return Equals(left, right); }
		public static bool operator !=(PfrSignature left, PfrSignature right) { return !Equals(left, right); }

		public Guid Id { get { return id; } }
		public Guid DocId { get { return docId; } }
		public SignatureType SignatureType { get { return signatureType; } }
		public int ContentLen { get { return contentLen; } }
		public long KansoOffset { get { return kansoOffset; } set { kansoOffset = value; } }

		private readonly Guid id;
		private readonly Guid docId;
		private readonly SignatureType signatureType;
		private readonly int contentLen;
		private long kansoOffset;
	}
}
