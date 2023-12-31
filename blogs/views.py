from itertools import count
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.views.generic import (
    TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import user_passes_test
from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http.response import HttpResponse
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from django.core.mail import send_mail
#from slick_reporting.views import SlickReportView
#from slick_reporting.fields import SlickReportField
from core.models import *
from .forms import *
from django.db.models import Count, Avg, Sum

class admin(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_admin
    
class employee(UserPassesTestMixin):
    
    def test_func(self):
        return self.request.user.is_employee

class BlogListView(LoginRequiredMixin, generic.ListView):
    template_name = "blogs/blog_list.html"
    queryset = Blog.objects.all().filter(status="PUBLISHED") # for published blogs
    #queryset = Blog.objects.all().filter(status=2)
    #queryset = Blog.objects.all()
    #queryset = CustomUser.objects.filter(user_type='blog') # not adding context here
    #CustomUser.objects.
    context_object_name = "blogs"
    paginate_by = 4

class BlogDraftListView(admin, generic.ListView):
    template_name = "blogs/blog_list_draft.html"
    queryset = Blog.objects.all().filter(status="DRAFT") # for published blogs
    #queryset = CustomUser.objects.filter(user_type='blog') # not adding context here
    #CustomUser.objects.
    context_object_name = "drafts"
    paginate_by = 4

class BlogArchivedListView(admin, employee, generic.ListView):
    template_name = "blogs/blog_list_archived.html"
    queryset = Blog.objects.all().filter(status="ARCHIVED") # for published blogs
    #queryset = CustomUser.objects.filter(user_type='blog') # not adding context here
    #CustomUser.objects.
    context_object_name = "archived"
    paginate_by = 4
    
        
class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "blogs/category_list.html"
    queryset = Category.objects.all() # not adding context here
    #queryset = CustomUser.objects.filter(user_type='blog') # not adding context here
    #CustomUser.objects.
    context_object_name = "category"
    paginate_by = 4

#creating permission, the below will be used for view the admin only could manage


#@user_passes_test(is_admin)
class BlogCreateView(admin, employee,  CreateView):
    template_name = "blogs/blog_create.html"
    form_class = BlogForm
    success_url = reverse_lazy('blogs:blog-list')
    
    
    def form_valid( self, form):
        form.instance.author = self.request.user
        form.instance.email = self.request.user.email
        return super().form_valid(form)

    
class CategoryCreateView(admin, employee, CreateView):
    template_name = "blogs/category_create.html"
    form_class = CategoryForm
    
    def get_success_url(self):
        return reverse("blogs:category-list")
      
def blog_detail(request, pk):
    blog = Blog.objects.get(pk=pk)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            reviews = Review(
                author=form.cleaned_data["author"],
                content=form.cleaned_data["content"],
                blog=blog
            )
            reviews.save()

    reviews = Review.objects.filter(blog=blog)
    #reply = Review.objects.filter(blog=blog).get(pk=pk)
    review_count = Review.objects.filter(blog=blog).annotate(num_reviews=Count("rating")).count()
    sum_rating = Review.objects.filter(blog=blog).aggregate(Sum("rating")) 
    average_rating = Review.objects.filter(blog=blog).aggregate(Avg("rating"))
    #replies = ReplyToReview.objects.filter(blog=blog, review=reply)
    average_rating = average_rating.get('rating__avg')# format the average rating
    average_rating = round(average_rating)# the whole number
   
    context = {
        "blog": blog,
        "reviews": reviews,
        #"replies": replies,
        "form": form,
        "review_count": review_count,
        "average_rating": average_rating,
        "sum_rating": sum_rating
        
    }

    return render(request, "blogs/blog_detail.html", context)

class BlogDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "blogs/blog_detail.html"
    queryset = Blog.objects.all() # not adding context here
    context_object_name = "blogs"

class BlogUpdateView(admin, employee, generic.UpdateView):
    template_name = "blogs/blog_update.html"
    form_class = BlogForm
    queryset = Blog.objects.all()
    
    def get_success_url(self):
        return reverse("blogs:blog-list")
    
    
    def form_valid(self, form):
        form.save()
        messages.info(self.request, "You have successfully updated this lead")
        return super(BlogUpdateView, self).form_valid(form)
    
   
class BlogDeleteView1(admin, generic.DeleteView):
    template_name = "blogs/blog_delete.html"
    queryset = Blog.objects.all()
    
    def get_success_url(self):
        return reverse("blogs:blog-list")


class BlogDeleteView(admin, generic.DeleteView):
    template_name = "blogs/blog_delete.html"
    queryset = Blog.objects.all()
    context_object_name = "delete_blogs"
    
    def get_success_url(self):
        return reverse("blogs:blog-list")

@login_required
def add_review(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            
            review.blog = blog
            review.user = request.user
            
            review.save()
            return redirect('blogs/blog_detail.html', pk=blog.pk)
    else:
        form = ReviewForm()
    return render(request, 'blogs/review_create.html', {'form': form, ' blog': blog})


   
class ReviewCreateView( LoginRequiredMixin, CreateView):
    model = Review
    fields = [ 'comment', 'rating']
    template_name = "blogs/review_create.html"
    success_url = reverse_lazy('blogs:blog-list')
     
    def form_valid(self, form):
        form.instance.reviewer = self.request.user
        #form.instance.email = self.request.user.email
        form.instance.blog = Blog.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)


class ReplyToReviewCreateView(CreateView):
    model = ReplyToReview
    #form_class = ReplyToReviewForm
    fields = [ 'comment']
    template_name = 'blogs/reply_create.html'
    success_url = reverse_lazy('blogs:blog-detail')

    def form_valid(self, form):
        form.instance.replier = self.request.user
        form.instance.review_id = Review.objects.get(pk=self.kwargs['review_id'])
        #form.instance.review = self.kwargs['review_id']
        
        return super().form_valid(form)

    #def get_success_url(self):
        #return reverse_lazy('blogs:review-detail', kwargs={'pk': self.kwargs['review_id']})

def send_reply( request, review_id):
    review = get_object_or_404(Review, id=review_id)
    form = ReplyToReviewForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            reply = form.save(commit=False)
            reply.replier= request.user
            reply.review = review
            reply.save()
            return redirect('blogs:blog-list')

    return render(request, 'blogs/reply_create.html', {'form': form, 'review': review})

class ReplyToReviewUpdateView(UpdateView):
    model = ReplyToReview
    form_class = ReplyToReviewForm
    template_name = 'blogs/reply_create.html'

    def get_success_url(self):
        return reverse_lazy('blogs:review-detail', kwargs={'pk': self.object.review_id})


class ReplyToReviewDeleteView(DeleteView):
    model = ReplyToReview
    template_name = 'replies/reply_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('review_detail', kwargs={'pk': self.object.review_id})
class BlogsSearchView(ListView):
    model = Blog
    template_name = "blogs/blog_search.html"

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        object_list = Blog.objects.filter(
            
            Q(title__icontains=query)| 
            Q(email__icontains=query)|
            Q(author__icontains=query)|
            Q(categories__icontains=query)|
            Q(status__icontains=query) |
            Q(created_on__icontains=query)
        )
        return object_list   
