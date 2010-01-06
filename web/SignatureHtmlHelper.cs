using System;
using System.Security.Cryptography.X509Certificates;
using System.Web;
#if MONO
    using ASN1=Mono.Security.ASN1;
#endif

namespace Kontur.WebPFR
{
	public class SignatureHtmlHelper
	{
		public string GetSignatureDescr_Pfr(byte[] bytes)
		{
			X509Certificate cert = FindCert(bytes);
			if (cert == null) return "Неопознанная подпись";

			string ou = GetField(cert.Subject, "OU");
			string cn = GetField(cert.Subject, "CN");
			return string.Format(ou != "" ? "{0} ({1})" : "{0}", cn, ou);
		}

		public string GetSignatureDescr_Org(byte[] bytes)
		{
			X509Certificate cert = FindCert(bytes);
			if (cert == null) return "Неопознанная подпись";

			return string.Format("{0} ({1})", GetField(cert.Subject, "SN"), GetField(cert.Subject, "CN"));
		}

		private string GetField(string str, string name)
		{
			// Разбор внаглую надо заменить разбором по стандарту ietf.
			int s = str.IndexOf(name + "=");
			if (s < 0) return "";
			s += name.Length + 1;
			int f = str.IndexOf(',', s);
			if (f < 0) return "";
			return str.Substring(s, f - s);
		}

#if !MONO
        X509Certificate FindCert(byte[] bytes)
        {
            try{return new X509Certificate(bytes);} catch(CryptographicException) {return null;}
        }
#else
        X509Certificate FindCert(byte[] bytes)
        {
            var asn1 = new ASN1(bytes);
            for(int i = 0; i < asn1.Count; i++) {
                try {return new X509Certificate(asn1[i].GetBytes());} catch{}
                for(int j = 0; j < asn1[i].Count; j++) {
                    try {return new X509Certificate(asn1[i][j].GetBytes());} catch{}
                    for(int k = 0; k < asn1[i][j].Count; k++) {
                        try {return new X509Certificate(asn1[i][j][k].GetBytes());} catch{}
                        for(int l = 0; l < asn1[i][j][k].Count; l++) {
                            try {return new X509Certificate(asn1[i][j][k][l].GetBytes());} catch{}
                            for(int m = 0; m < asn1[i][j][k][l].Count; m++) {
                                try {return new X509Certificate(asn1[i][j][k][l][m].GetBytes());} catch{}
            }}}}}
            return null;
        }
#endif
	}
}
