/* 
    I adapted this function from this post: https://www.w3schools.com/howto/howto_js_copy_clipboard.asp
    but evidently I didn't do it right because it doesn't work
    and it turns out I didn't need it anyway ;)
 */

function copyButton() {
    const copyText = document.getElementById('copy-content')
    copyText.select();
    document.execCommand('copy');
}

