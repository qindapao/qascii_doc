# qascii_doc
Personal asciidoc build system

## editor

we can use [asciidocfx](https://asciidocfx.com/) or `vim`.

`asciidocfx`需要安装完整的`java`环境，我并不是很喜欢，所以还是选择用`vim`来编辑。
然后用自定义的模板来预览，如果导出使用官方的标准的`Ruby`工具。

`asciidoc`的工具链并没有`Sphinx`强大，很多东西需要自己动手。


## 环境准备

### ruby

#### 环境安装

如果最新的版本有问题，可以在这里下载历史版本，`3.2.9`这个版本是比较稳定的。

https://rubyinstaller.org/downloads/archives/

#### asciidoctor 安装

推荐使用`gitbash`来安装，比较方便，如果需要设置代理，可以先：

```bash
export http_proxy=http://用户名:密码@proxy.xx.com:8080 
```

如果密码中有特殊字符，参考[URL编码对照表](https://config.net.cn/tools/UrlEncodeCode.html).

```bash
gem install asciidoctor
gem install asciidoctor-pdf
gem install asciidoctor-pdf-cjk-kai_gen_gothic
```

### 预览环境准备

进入到需要预览的文件的目录，然后通过`python`开启服务器。

```bash
python -m http.server
```

`vim`中定义这样的函数：

```vim
function! PreviewAsciiDoc()
    let l:filename = expand('%:t')
    let l:url = 'http://localhost:8000/asciidoc_preview.html?file=' . l:filename
    " 前提是浏览器的路径要在环境变量中
    call job_start(['chrome', l:url])
    " call job_start(['msedge', l:url])
endfunction
nnoremap <leader><leader>p :call PreviewAsciiDoc()<CR>
```

我们在vim中编辑一个文件的时候，就可以调用自定义的函数来通过浏览器打开模板来预览
我们的文件。模板会自动检测源文件的更新，当文件更新的时候，预览页会同步更新。

## 导出

### 导出到html

#### 一般的可选参数

如果源文件头部是：`:toc: left`，那么目录自动固定在左边。或者命令行加参数也可以。

命令行参数中的 `-a` 标签其实就是源文件头部的 `::` 属性信息。为了简化命令行参数，
我们常见的做法就是直接写到源文件头部，这样也好控制。

```bash
asciidoctor -b html5 -a toc=left -a toclevels=6 -a sectnums demo.adoc
```

或者直接：

```bash
asciidoctor -b html5 demo.adoc -o demo.html
```

#### 定制自己的样式

1. 这个属于高级玩法了。可以定义一个`custom.css`，放置到和源文件相同的目录下。
2. 如果有 `javascript` 脚本需要定制，那么定义一个 `docinfo.html` 在相同目录下，
里面写入注入的 `javascript` 代码。源文件头加上。

```asciidoc
:stylesheet: custom.css
:docinfo: shared
```

然后导出的时候可以不指定任何参数，因为我们已经在源文件中指定了。

```bash
asciidoctor -b html5 demo.adoc -o demo_custom.html
```

当前场景下，定义成`docinfo-header.html`也是可以的。

其实有三个文件可以注入：

* docinfo.html
    插入到 `<body>` 中，JS 脚本、版权声明、页脚信息等

* docinfo-footer.html
    插入到 `<body>` 末尾，JS 脚本、目录栏容器、初始化逻辑等

* docinfo-header.html
    插入到 `<head>` 中，`<style>`、`<meta>`、外部 `CSS/JS` 引入等
3. 如果想指定某个 `javascript` 注入脚本为某个文档专用，源文件头像下面这样写。

```asciidoc
:stylesheet: custom.css
::docinfo: private
```

然后我们的注入脚本命名为： `yourdocname-docinfo.html`、
`yourdocname-docinfo-footer.html`、`yourdocname-docinfo-header.html`。
在我们当前的项目中，就命名为：`demo-docinfo.html`。
这样的好处是我们可以为每个文档定制主题。

注意：当前定制样式只在 `html` 中有效，在 `pdf` 中默认是无效的。所以如果要转换成
pdf 建议文档中不要使用自定义语法。


### 导出到pdf

#### 导出基础

* 通过命令行进入到我们的源文件目录。

```bash
[user@~]$ cd /f/asciidoc_learn/asciidoc/
[user@asciidoc]$ 
```

* 运行导出命令

如果源文件中有**中文**，默认情况下可能无法正常导出。我们需要指定中文字体文件。


1. 找到`asciidoctor-pdf-cjk-kai_gen_gothic`的安装目录。

```txt
C:\ruby\lib\ruby\gems\3.2.0\gems\asciidoctor-pdf-cjk-kai_gen_gothic-0.1.1
```

可以用`everything`软件来搜索。

2. 进入`data/themes/`目录 把`KaiGenGothicCN-theme.yml`复制成`default-theme.yml`。

* 需要下载的第一种字体：更纱黑体[Sarasa-Gothic](https://github.com/be5invis/Sarasa-Gothic)。

```txt
SarasaMonoK-Regular.ttf
SarasaMonoSC-Bold.ttf
SarasaMonoSC-BoldItalic.ttf
SarasaMonoSC-Italic.ttf
```

* 需要下载的第二种字体：然后还有下载一种字体：[RobotoMono](https://github.com/googlefonts/RobotoMono)。

```txt
RobotoMono-Regular.ttf
RobotoMono-BoldItalic.ttf
```

然后把我们下载的`6个`字体文件放置到：`data\fonts`目录，然后把相应的字体改名。
规则如下：

```txt
SarasaMonoSC-Regular.ttf         ---->     KaiGenGothicCN-Regular.ttf
SarasaMonoSC-Bold.ttf            ---->     KaiGenGothicCN-Bold.ttf
SarasaMonoSC-BoldItalic.ttf      ---->     KaiGenGothicCN-Bold-Italic.ttf
SarasaMonoSC-Italic.ttf          ---->     KaiGenGothicCN-Regular-Italic.ttf
RobotoMono-Regular.ttf           ---->     RobotoMono-Regular.ttf
RobotoMono-BoldItalic.ttf        ---->     RobotoMono-BoldItalic.ttf
```

如果你喜欢 [KaiGenGothic](https://github.com/chloerei/asciidoctor-pdf-cjk-kai_gen_gothic/releases/tag/v0.1.0-fonts) 字体，直接下载这个字体也行，不过我感觉这个字体太老旧了，
就用`sarasamono`来替代它了。

3. 然后运行下面的命令导出`pdf`.

1). 第一种方式导出(中文需要加载自己的插件，所以用`asciidoctor`)

```bash
asciidoctor -r asciidoctor-pdf-cjk-kai_gen_gothic -a scripts=cjk -b pdf demo.adoc -o demo.pdf
```

2). 第二种方式导出(全英文的文档使用`asciidoctor-pdf`更加好看，它用自己的主题)

```bash
asciidoctor-pdf demo.adoc -o demo.pdf
```

***TIPS***:

1. 如果你希望自定义字体或主题，可以使用 `-a pdf-theme=xxx.yml -a pdf-fontsdir=xxx` 参数
2. 中文文档建议加上 `-a scripts=cjk`，改善标点与换行表现
3. 如果文档中包含中文和英文混排，可以考虑混合使用 `fallback` 字体配置

#### 多文件导出

1. 使用脚本一次性导出多个文件。

可以类似下面这样：

```bash
for file in *.adoc; do
    asciidoctor-pdf "$file" -o "${file%.adoc}.pdf"
done
```


2. 多文件相互链接怎么办。

* `AsciiDoc` 支持使用 `xref:` 来创建跨文档链接，这在 HTML 输出中是有效的。

```Asciidoc
xref:chapter2.adoc[下一章]
```

* `pdf`是不支持跨文件的链接的。
    * `pdf` 不支持跳转到另一个 `pdf` 文件内部的锚点。
    * `xref:` 在 PDF 中会被渲染为普通文本或不可点击的链接。
    * 如果你导出的是多个 `pdf` 文件，它们之间无法实现跳转。

推荐做法：合并为一个 PDF 文件。
如果你希望链接能跳转成功，建议将多个 `.adoc` 文件合并为一个主文档：


```Asciidoc
= 我的文档合集

include::chapter1.adoc[]
include::chapter2.adoc[]
include::chapter3.adoc[]
```

然后只导出这个主文档：

```bash
asciidoctor-pdf main.adoc -o all-in-one.pdf
```

这样所有 `xref:` 链接都能在 PDF 内部跳转，目录也能自动生成。


#### 相对路径和绝对路径

AsciiDoc 默认使用 相对路径 来解析 `include::` 和 `xref:`，例如：

```asciidoc
include::chapters/chapter1.adoc[]
xref:chapters/chapter2.adoc[第二章]
```

只要你的文件结构保持一致，链接就能正确解析。

#### 取巧的方法(推荐)

如果要保持 `html` 中所有的格式，包括自定义的格式，那么可以通过浏览器的`打印`
功能中的`打印到PDF`来实现。

但是直接打印出来的 `pdf` 的页眉和页脚没法控制，并且还有别的东西也无法改。
我们考虑使用`Puppeteer`。

1. 安装 Puppeteer

确保你已经安装了 `Node.js`，然后运行下面的命令安装`puppeteer`包：

```bash
export PUPPETEER_SKIP_DOWNLOAD=true
npm install -g puppeteer
```

>上面一定要加 `-g` 选项把工具安装到全局环境中去，不要安装到当前目录下。

2. 运行导出命令，从`html`中转换到`pdf`。

```bash
node export-pdf.js input=demo.html output=demo.pdf size=A3 title="技术文档"
```

3. 导出的`pdf`尽量保持了原始的格式，但是没有侧边栏的`toc`功能。可以用下面的
`python`脚本来生成，运行脚本前先编辑`generate_pdf_outline.json`文件配置参数。

```python
pip install pymupdf

python generate_pdf_outline.py
```



### 转换成高级的PDF的方法

https://blog.csdn.net/gitblog_01071/article/details/142509412

暂时没有研究。

## snippet

### vim

如果使用的是`vim`编辑器，可以使用当前项目中的`asciidoc.snippets`文件来做语法补全。

一般情况下放置到`C:\Users\xx\.vim\plugged\vim-snippets\mysnips`目录即可。具体取决于你的配置。
如果经常更新，最好的方法是直接从项目目录创建一个`link`到vim的相应插件目录。`Windows`系统
请在`cmd`环境下执行下面的指令，不要在`power shell`的环境中执行。

```cmd
C:\Windows\System32>C:

C:\>cd C:\Users\xx\.vim\plugged\vim-snippets\mysnips\

C:\Users\xx\.vim\plugged\vim-snippets\mysnips>mklink asciidoc.snippets D:\project\asciidoc\asciidoc.snippets
为 asciidoc.snippets <<===>> D:\project\asciidoc\asciidoc.snippets 创建的符号链接

C:\Users\xx\.vim\plugged\vim-snippets\mysnips>
```

如果你不怕麻烦，每次更新后手动拷贝过去也是可以的。


