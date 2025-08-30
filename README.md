In development - 
[TODO](https://github.com/search?q=repo%3Aclorteau%2Farch-wiki-search%20TODO&type=code)s



## Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal ##

*💡The idea is to always have access to your important wikis, even when things are so FUBAR there's no graphical environment or internet, in an easy to read way, and also to reduce the load on the wiki hoster themselves since users would be using their own cache most of the time.*

It caches what you access +1 level of links if needed on the fly while you have a network connection, and accesses the cache when you're offline or the cache needs a refresh. It can also simplify the pages on the fly and export and import caches for out-of-band sharing or inclusion in an install media. 

There's no option to cache a whole wiki at once, in order to, you know, *not* DDOS them. So what will be available offline will be what you already accessed online manually, or that you imported with --merge prior.

### Start up ###
`$ arch-wiki-search "installation guide"`

> [!NOTE]
> As of today (2025-08-27) this is early development and the default wiki is \'archwiki\' because this started as a quick python script for me to load archwiki whenever needed. This tool is meant to read any useful wiki.

> [!TIP]
> The option --wiki has a number of pre-defined wikis and you\'re invited to add your own through this [templated bug request](https://github.com/clorteau/arch-wiki-search/issues/new?template=new-wiki.md), a [config file](https://github.com/clorteau/arch-wiki-search/blob/main/arch_wiki_search/wikis.yaml) or command-line arguments

For instance:

`$ arch-wiki-search --wiki=wikipedia --conv=txt "MIT license"`

> [!TIP]
>
> The option --conv converts the pages in more readable formats:
> raw: no conversion (but still remove binaries)
> clean: convert to cleaner HTML (remove styles and scripts)
> basic: convert to basic HTML
> md: convert to markdown
> txt: convert to plain text
[TODO: screenshots/webms]
 
From there, it will:
- Spin its own little local web server that will send you the pages you request, while getting them either from:
	+ Its own saved copy
	+ The server

Therefore if you're offline and you already visited this when on-line, you will not see a difference 🤞

- Save/refresh the cached copy
  
It's a caching web proxy that caches for a very long time and simplifies the pages so it's called [LazyProxy](https://github.com/clorteau/arch-wiki-search/blob/documentation/arch_wiki_search/cachingproxy.py)

- Search for the most appropriate available browser to load for your environment, such as 'elinks' if you're on SSH for instance, or the user's defined default browser if there's a desktop environment, and call it
- If a graphical environment is available and PyQT is installed, spawn a 📚 notification area icon where you can access the wiki directly

So in one command / couple clicks you get what you were looking for on your wiki in your favorite browser from your own offline copy that gets updated as, and only if, needed. If that's not your experience, [file a bug](https://github.com/clorteau/arch-wiki-search/issues).

You can elso export and import whole caches for off-band sharing or inclusion in an install media for instance.

More details in `--help`.

This is all Python using common libraries and is a proper PyPI package itself, so it's compatible Linux (all distros), MacOS and Windows and available through all these through PyPI - again, despite the name. From there standard packaging helpers plug in easily. At the moment the only such package available is an Arch package through AUR. 

### Installation ###

#### Arch Linux and derivatives through AUR - with [yay](https://github.com/Jguer/yay): ####
```bash
$ yay -S arch-wiki-search
```

#### Linux, Windows, MacOS through PyPI - with [pipx](https://pipx.pypa.io/latest/installation/): ####
```bash
$ pipx install arch-wiki-search
```


### Help ###
```bash
$ arch-wiki-search --help
usage: arch-wiki-search [-h]
                          [-w {archwiki,discovery,fedorawiki,freebsdwiki,gentoowiki,manjarowiki,pythonwiki,slackdocs,wikipedia}]
                          [-u URL] [-s SEARCHSTRING] [-c {raw,clean,basic,md,txt}] [--offline]
                          [--refresh] [-v] [-x] [-m MERGE] [-ni] [--clear] [-d]
                          [search]

Read and search Archwiki and other wikis, online or offline, in HTML, markdown or text, on the desktop or the terminal 

Examples:
    🡪 $ arch-wiki-search "installation guide"
    🡪 $ arch-wiki-search --wiki=wikipedia --conv=txt "MIT license"

positional arguments:
  search                string to search (ex: "installation guide")

options:
  -h, --help            show this help message and exit
  -w, --wiki {archwiki,discovery,fedorawiki,freebsdwiki,gentoowiki,manjarowiki,pythonwiki,slackdocs,wikipedia}
                        Load a known wiki by name (ex: --wiki=wikipedia) [Default: archwiki]
  -u, --url URL         URL of wiki to browse (ex: https://fr.wikipedia.org, https://wiki.freebsd.org)
  -s, --searchstring SEARCHSTRING
                        alternative search string (ex: "/wiki/Special:Search?go=Go&search=", "/FrontPage?action=fullsearch&value=")
  -c, --conv {raw,clean,basic,md,txt}
                        conversion mode:
                        raw: no conversion (but still remove binaries)
                        clean: convert to cleaner HTML (remove styles and scripts)
                        basic: convert to basic HTML
                        md: convert to markdown
                        txt: convert to plain text
                        [Default: 'raw' in graphical environment, 'basic' otherwise]
  --offline, --test     Don't try to go online, only use cached copy if it exists
  --refresh             Force going online and refresh the cache
  -v, --version         Print version number and exit
  -x, --export          Export cache as .zip file
  -m, --merge MERGE     Import and merge cache from a zip file created with --export
  -ni, --noicon         Don't show the 📚 notification area icon - only <ctrl+c> will stop
  --clear               Clear cache and exit
  -d, --debug

Options -u and -s overwrite the corresponding url or searchstring provided by -w
Known wiki names and their url/searchstring pairs are read from a 'wikis.yaml' file in '$(pwd)' and '{$HOME}/.config/arch-wiki-search'
Github: 🌐https://github.com/clorteau/arch-wiki-search
Request to add new wiki: 🌐https://github.com/clorteau/arch-wiki-search/issues/new?template=new-wiki.md
```
