# qascii_doc
Personal asciidoc build system

## editor

we can use [asciidocfx](https://asciidocfx.com/) or `vim`.

`asciidocfx`需要安装完整的`java`环境，我并不是很喜欢，所以还是选择用`vim`来编辑。
然后用自定义的模板来预览，如果导出使用官方的标准的`Ruby`工具。

## 环境准备

### ruby

#### 环境安装

如果最新的版本有问题，可以在这里下载历史版本，`3.2.9`这个版本是比较稳定的。

https://rubyinstaller.org/downloads/archives/

#### asciidoctor 安装

推荐使用`gitbash`来安装，比较方便，如果需要设置代码，可以先：

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

如果你喜欢 `KaiGenGothic` 字体，直接下载这个字体也行，不过我感觉这个字体太老旧了，
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

### 导出到html

#### 目录位置

如果源文件头部是：`:toc: left`，那么目录自动固定在左边。或者命令行加参数也可以。

```bash
asciidoctor -a toc=left -a toclevels=6 -a sectnums demo.adoc
```

#### 定制自己的样式

这个属于高级玩法了。比如我们想实现浮动的侧边目录，可以定义一个`custom.css`，放置到和源
文件相同的目录下。

```css
.toc {
    position: fixed;
    left: 0;
    top: 0;
    width: 250px;
    height: 100%;
    overflow-y: auto;
    background-color: #f9f9f9;
    border-right: 1px solid #ccc;
    transition: transform 0.3s ease;
    transform: translateX(-100%);
    z-index: 999;
}

.toc:hover {
    transform: translateX(0);
}
```

然后导出的时候这样(支持绑定多个`css`文件)：

```bash
asciidoctor -a toc=left -a linkcss=true -a stylesdir=. -a stylesheet=asciidoctor-default.css,custom.css demo.adoc -o custom.html
```
#### 脚本注入

一些参考文档：

* https://liming.pub/post/asciidoctor-customization/
* https://docs.asciidoctor.org/asciidoctor/latest/html-backend/custom-stylesheet/

##### 源文件中的操作

```Asciidoc
:docinfo: shared
```

`:docinfo: shared` 的作用: 它会在导出的 HTML 中插入一个名为：
`<basename>-docinfo.html`
的文件内容，位置在 `<head>` 标签内。比如你的文档叫 `demo.adoc`，那它就会去找：
`demo-docinfo.html`，并把里面的内容嵌入到 HTML 的 `<head>` 区域。



##### 注入脚本编辑

参考`demo-docinfo.html`。

##### 命令行导出参数

```bash
asciidoctor -a docinfo=shared -a stylesheet=asciidoctor-default.css,custom.css -a linkcss=true demo.adoc -o demo_insert.html
```

##### 变通的方法

当前这些方案如果实现复杂，其实可以写一个脚本。在导出源文件以前，先创建一个分支，
把源文件中的特殊标签都处理掉。然后再用标准的转换流程处理即可。只是这样太麻烦了，
有空还是研究清楚上面的方法。


##### 转换成高级的PDF的方法

https://blog.csdn.net/gitblog_01071/article/details/142509412

