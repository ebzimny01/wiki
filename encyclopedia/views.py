from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms
import random
from markdown2 import Markdown
from . import util
quit

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def title(request, title):
    contents = util.get_entry(title)
    if contents == None:
        return render(request, "encyclopedia/entry.html", {
            "contents": "Requested page not found.",
            "title": "Error:"
        })
    else:
        markdowner = Markdown()
        contents_converted = markdowner.convert(contents)
        return render(request, "encyclopedia/entry.html", {
            "contents": contents_converted,
            "title": title
        })

def search(request):
    query = request.GET['q']
    entries = util.list_entries()
    sublist = []
    for text in entries:
            if query.lower() in text.lower():
                sublist.append(text)
    for i in range(len(entries)):
        entries[i] = entries[i].lower()
    if query.lower() in entries:
        url = '{}{}'.format("wiki/", query)
        return redirect(url)
    elif len(sublist) > 0:
        return render(request, "encyclopedia/search.html", {
            "search_results": sublist,
            "message": "Search for '" + query + "' returned:"
        })
    else:
        return render(request, "encyclopedia/search.html", {
            "message": "Wiki entry of that name does not exist."
        })

class NewPageForm(forms.Form):
    pagetitle = forms.CharField(label="Title", min_length=1, max_length=255, strip=True, required=True)
    pagecontent = forms.CharField(label="Content", widget=forms.Textarea, min_length=1, required=True)

def newpage(request):
    # Check if method is POST
    if request.method == "POST":
        
        # Take in the data the user submitted and save it as form
        form = NewPageForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the title and content from the 'cleaned' version of form data
            title = form.cleaned_data["pagetitle"]
            content = form.cleaned_data["pagecontent"]
            entries = util.list_entries()
            for i in range(len(entries)):
                entries[i] = entries[i].lower()
            # If the title already matches an existing entry, re-render the page with existing information.
            if title.lower() in entries:
                return render(request, "encyclopedia/newpage.html", {
                    "form": form,
                    "message": "A wiki entry with that title already exists. Please pick a unique title."
                })
            else:
                # save the new entry and redirect to the new page
                util.save_entry(title, content)
                url = '{}{}'.format("wiki/", title)
                return redirect(url)
        else:
            # If the form is invalid, re-render the page with existing information.
            return render(request, "encyclopedia/newpage.html", {
                    "form": form,
                    "message": "Invalid form entry."
                })

    # If GET request then render New Page Form            
    return render(request, "encyclopedia/newpage.html", {
        "form": NewPageForm()
    })

class EditPageForm(forms.Form):
    # used to get the page content to edit
    pagecontent = forms.CharField(label="Content", widget=forms.Textarea())

def editpage(request, title):
    if request.method == 'GET':
        entry = util.get_entry(title)
        content_to_edit = EditPageForm(initial={'pagecontent': entry})
        return render(request, "encyclopedia/editpage.html", {
            "title": title,
            "content_to_edit": content_to_edit
        })
    else:
        # Take in the data the user edited and save it as form
        form = EditPageForm(request.POST)
        
        # Check if form data is valid (server-side)
        if form.is_valid():
            # save the new entry and redirect to the new page
            editedcontent = form.cleaned_data["pagecontent"]
            util.save_entry(title, editedcontent)
            url = '{}{}'.format("/wiki/", title)
            return redirect(url)

def randompage(request):
    entries = util.list_entries()
    randompage = random.choice(entries)
    url = '{}{}'.format("/wiki/", randompage)
    return redirect(url)