In development - 
[TODO](https://github.com/search?q=repo%3Aclorteau%2Farch-wiki-search%20TODO&type=code)s



## Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal ##

*💡The idea is to always have access to your important wikis, even when things are so FUBAR there's no graphical environment or internet, and also to reduce the load on the wiki hoster themselves since users would be using their own cache most of the time.*

It launches the browser appropriate to your environment, caches what you access +1 level of links if needed on the fly while you have a network connection, and accesses the cache when you're offline or the cache needs a refresh. It can also simplify the pages on the fly and export and import caches for out-of-band sharing or inclusion in an install media. 

There's no option to cache a whole wiki at once, in order to, you know, *not* DDOS them. So what will be available offline will be what you already accessed online manually, or that you imported with --merge prior.

For instance:

`$ arch-wiki-search "installation guide"`

`$ arch-wiki-search --wiki=wikipedia --conv=txt "MIT license"`

[TODO: screenshots/webms]
 
See --help:


```bash
$ arch-wiki-search [-h] [-w {archwiki,discovery,fedorawiki,freebsdwiki,manjarowiki,pythonwiki,slackdocs,wikipedia}]
                             [-u URL] [-s SEARCHSTRING] [-c {raw,clean,txt}] [--offline] [--refresh] [-v] [-x] [-m MERGE] [-d]
                             [search]

Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal

Examples:
    🡪 $ arch-wiki-search "installation guide"
    🡪 $ arch-wiki-search --wiki=wikipedia "MIT license"

positional arguments:
  search                string to search (ex: "installation guide")

options:
  -h, --help            show this help message and exit
  -w, --wiki {archwiki,discovery,fedorawiki,freebsdwiki,manjarowiki,pythonwiki,slackdocs,wikipedia}
                        Load a known wiki by name (ex: --wiki=wikipedia) [Default: archwiki]
  -u, --url URL         URL of wiki to browse (ex: https://wikipedia.org, https://wiki.freebsd.org)
  -s, --searchstring SEARCHSTRING
                        alternative search string (ex: "/wiki/Special:Search?go=Go&search=", "/FrontPage?action=fullsearch&value=")
  -c, --conv {raw,clean,txt}
                        conversion mode:
                        raw: no conversion (but still remove binaries)
                        clean: convert to simple html (basic formatting, no styles or scripts)
                        txt: convert to plain text
                        [Default: 'raw' in graphical environment, 'clean' otherwise]
  --offline, --test     Don't try to go online, only use cached copy if it exists
  --refresh             Force going online and refresh the cache
  -v, --version         Print version number and exit
  -x, --export          Export cache as .zip file
  -m, --merge MERGE     Import and merge cache from a zip file created with --export
  -d, --debug

Options -u and -s overwrite the corresponding url or searchstring provided by -w
Known wiki names and their url/searchstring pairs are read from a 'wikis.yaml' file in '$(pwd)' and '{$HOME}/.config/arch-wiki-search'
Github: 🌐https://github.com/clorteau/arch-wiki-search
Request to add new wiki: 🌐https://github.com/clorteau/arch-wiki-search/issues/new?template=new-wiki.md
```

### Installation ###

#### Arch Linux and derivatives through AUR ####
```bash
$ yay -S arch-wiki-search
```

#### Anywhere through PyPI ####
```bash
$ pipx install arch-wiki-search
```
