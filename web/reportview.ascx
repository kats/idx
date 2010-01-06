<%@ Control Language="C#" AutoEventWireup="true" Inherits="Kontur.WebPFR.reportview" %>
<div id="reportView">
	<script type="text/javascript">
		reportC = {
			load: function() {
				$("#reportView #saveSignatures").click(reportC.saveSignatures);
			},
			loadUrlSync: function(url) {
				return $.ajax({
					async: false,
					dataType: "text",
					processData: false,
					type: "GET",
					url: url,
					error: function(event, XMLHttpRequest, ajaxOptions, thrownError) { }
				}).responseText;
			},
			saveSignatures: function() {
				var comDialogs = new ActiveXObject("Kontur.ComDlgs");
				var bin = new ActiveXObject("SKBKontur_LIT_CryptoCOM.BinaryObjectService");

				var folder = comDialogs.SelectFolderDialog();
				if (folder === null || folder == "") return;

				var reName = /&filename=([^&]*)/;
				var reType = /&type=([^&]*)/;

				$("#reportView a.sign").each(function(i, el) {
					var h = el.href;
					var name = reName.exec(h)[1];
					var type = reType.exec(h)[1];
					var bo = bin.BinaryObjectFromBase64(
						reportC.loadUrlSync(h.substring(h.search("signature.ashx")).replace("mode=sign", "mode=b64")));
					bin.BinaryObjectToFile(bo, reportC._utf8_decode(unescape(folder + "\\" + name + "." + type + ".sign")));
				});
			},
			_utf8_decode: function(utftext) {
				var string = "";
				var i = 0;
				var c = c1 = c2 = 0;

				while (i < utftext.length) {
					c = utftext.charCodeAt(i);
					if (c < 128) {
						string += String.fromCharCode(c);
						i++;
					}
					else if ((c > 191) && (c < 224)) {
						c2 = utftext.charCodeAt(i + 1);
						string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
						i += 2;
					}
					else {
						c2 = utftext.charCodeAt(i + 1);
						c3 = utftext.charCodeAt(i + 2);
						string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
						i += 3;
					}
				}
				return string;
			}
		}
	</script>
	<h2>Отправленные сведения</h2>
	<ol id="files">
		<%=GetFilesHtml()%>
	</ol>
	<span class="signature">Подписаны: <a href="#"><%=GetSignature()%></a></span> 
</div>
