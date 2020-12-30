const opts = require("./auth");
const exec = require('child_process').exec;
const http = require('http')
const fetch = require('node-fetch')
const crypto = require('crypto')
const path = require("path");
const express = require('express')
const bp = require('body-parser')
const app = express()
app.use(bp.json())
//send("CI BOT", "", [{ title: "CI Bot Reload", description: "The CI/CD Bot has started" }])
//The following server code is taken from https://www.robinwieruch.de/github-webhook-node-js
app.post("/", (req, res)=>{
    console.log("Got Data")
    const signature = `sha1=${crypto
        .createHmac('sha1', opts.ghwebhooksecret)
        .update(JSON.stringify(req.body))
        .digest('hex')}`;

    const isAllowed = req.headers['x-hub-signature'] === signature;
    try {
        
        const isMaster = req.body.ref === 'refs/heads/master';
        if (isAllowed && isMaster) {
            initBuild(req.body)
        }
    } catch (e) {
        console.log(e)
    }
    res.status(200).send("OK")
})
app.get("/logs", (req, res)=>{
    //todo: use name from docker-compose.yml
    exec("docker logs 1405bot | tail -n 1000 | perl -e 'print reverse <>'", function callback(udErr, udOut, udStdErr) {
	res.setHeader('Content-Type', 'text/plain');
        if (true == (udErr || udStdErr)) {
            console.log("Pull err")
            res.status(500).send(`Error Pulling Logs: \n ${udErr} \n ${udStdErr}`)
        }
        else if (udOut){
            udOut = udOut.replace(/^\*\*.*$/gm, "--Line Removed From Logs--")
            res.status(200).send(`Got Logs: \n ${udOut}`)

        } else {
            res.status(500).send("Something happened.")
        }

})})
app.listen(6810);

function send(username, body, embeds) {
    fetch(`https://discordapp.com/api/webhooks/${opts.updateChannel}/${opts.webhookKey}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            content: body,
            username: username,
            embeds: embeds
        })
    })
}
function initBuild(body) {
//    console.log(body)
console.log("Start")

    function resolveCodeBlock(error, stdout, stderr) {
        let cmdRes = stdout ? stdout : ""
        if (error && !stderr)
            cmdRes += "\nUnknown Error"
        else if (stderr)
            cmdRes += stderr
        if (!cmdRes)
            return ""
        //For those that don't speak regex-ese, this takes the first 1900 chars
        return cmdRes.match(/(.|\n){0,1900}/s)[0]
    }
    send("Commit Notifier", "", [
        {
            title: `Commit - ${body.after}`,
            url: body.head_commit.url,
            description: "A commit has occured on the master branch. Pulling now."
        }
    ])
    exec(path.resolve(__dirname, 'scripts', 'update.sh'), function callback(udErr, udOut, udStdErr) {
        if (true == (udErr || udStdErr)) {
            console.log("Pull err")
            return send("Update Notifier", "", [
                {
                    title: `Commit - ${body.after}`,
                    description: `Error whild updating repo: \n \`\`\`\n${resolveCodeBlock(udErr, udOut, udErr)} \`\`\``
                }
            ])

        }
        send("Update Notifier", "", [
            {
                title: `Commit -  ${body.after}`,
                description: "This commit has been pulled. Building Now"
            }
        ])

        exec(`BOT_TOKEN=${opts.runBot} BOT_CHAN=${opts.runChan} ` + path.resolve(__dirname, 'scripts', 'build.sh'), function callback(bdErr, bdStdOut, bdStdErr) {
            if (true == (bdStdErr || bdErr)) {
                console.log("Build err")

                return send("Build Notifier", "", [
                    {
                        title: `Commit - ${body.after}`,
                        description: "This commit has faild to build"
                    }
                ])
            }
            console.log("Build good")

            send("Build Notifier", "", [
                {
                    title: `Commit - ${body.after}`,
                    description: `Built: \n \`\`\`\n${resolveCodeBlock(bdErr, bdStdOut, bdStdErr)} \`\`\``
                }
            ])


        });
    });




}
