from gi.repository import Gtk, GObject, GdkPixbuf
from webcrawler import showBooks
from time import gmtime, strftime
from exam import listTT
from notes import uploadFile, listUploads, downloadFile
from bookLending import *
import webbrowser

def semFinder(roll): #simple function to parse the roll number and get sem
	a=str(roll)
	year=a[0:2]
	m=strftime("%m", gmtime())
	y=strftime("%y", gmtime())
	ans = ((float(m)-1)/12)+int(y)-int(year)
	return int(ans*2)

def depFinder(roll): #simple function to parse the roll number and get dept.

	a=str(roll)
	dep=a[4:6]
	deps={"01":"CSE","02":"ECE","03":"ME","04":"CE","05":"bdes","06":"BT","07":"CL","08":"EEE","21":"EPh","22":"CST","23":"MC"}
	return deps[dep]

def displayResult(dept, sem, roll): #result display fuction
	win = MainNotebook(dept,sem,roll) #calling notebookview
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	win.textBox.hide()
	win.rating_combo.hide()
	win.button_rating.hide()
	win.button_lend.hide()
	win.button_submit_lend.hide()
	win.contact_field.hide()
	win.button_delete.hide()
	Gtk.main()


class MainNotebook(Gtk.Window):

	def __init__(self,dept="CSE",sem=3,roll='140101063'):
		Gtk.Window.__init__(self, title="Acad-Hub")
		# self.set_resizable(True)
		# self.maximize()
		# self.set_default_size(300, 300)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_border_width(10)
		WindowBox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		self.notebook = Gtk.Notebook() #init. new notebook view
		WindowBox.pack_start(self.notebook,True,True,0)

		self.notebook.set_scrollable(True)

		courseBooks = showBooks(dept, sem) #getting an array of coursebooks and rel. info
		self.page1 = Gtk.Box() 
		self.page1.set_border_width(10)
		books_list_store = Gtk.ListStore(str, str, str, str, str, str,str) #new liststore for books
		for book in courseBooks:
			books_list_store.append(list(book))

		books_tree_view = Gtk.TreeView(books_list_store) #adding to treeview
	

		#adding columns
		for i, col_title in enumerate(["Course", "Code", "Title", "Author", "Publications/Edition", "Library Availability"]):
			renderer = Gtk.CellRendererText()
			renderer.set_fixed_size(-1,50)
			renderer.set_property('editable', True)
			
			column = Gtk.TreeViewColumn(col_title, renderer, text=i)
			column.add_attribute(renderer, "markup", i) 
			if i!=1:
				column.set_max_width(250)
				column.set_resizable(True)
				column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
				column.set_fixed_width(150)
			# column.set_sort_column_id(i) #allowing sortable columns
			books_tree_view.append_column(column) 
		

		

		self.page1.pack_start(books_tree_view, True, True, 0)

		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)



		padding_box=Gtk.Box()
		padding_box.set_size_request(20,20)
		vbox.pack_start(padding_box, False, False, 0)


		for book in courseBooks:
			if book[6]=="None":
				button = Gtk.LinkButton(book[6],label="Not Available")
				button.set_size_request(20,54)
				vbox.pack_start(button, False, False, 0)
			else:
				button = Gtk.LinkButton(book[6],label="Download")
				button.set_size_request(20,54)
				vbox.pack_start(button, False, False, 0)

		self.page1.pack_start(vbox,False,False,0)

		self.notebook.append_page(self.page1, Gtk.Label('Books Info'))
		#adding books page

		self.page2 = Gtk.Box()
		self.page2.set_border_width(10)
		examtt= listTT(dept,sem) #fetching exam time table array
		exams_list_store = Gtk.ListStore(str,str, str,str,str,str) #creating liststore for the same
		for exam in examtt:
			exams_list_store.append(list(exam))

		exams_tree_view = Gtk.TreeView(exams_list_store)
		exams_tree_view.columns_autosize()

		for i, col_title in enumerate(["Course", "Course Name","Day","End-Sem Date","End-Sem Day", "Venue"]): #rendering data
			renderer = Gtk.CellRendererText()

			column = Gtk.TreeViewColumn(col_title, renderer, text=i)
			column.set_sort_column_id(i)

			exams_tree_view.append_column(column)

		self.page2.pack_start(exams_tree_view, True, True, 0)
		self.notebook.append_page(self.page2, Gtk.Label('Exam Time Table'))

		#adding exam time table

		self.page3 = Gtk.Box()
		self.page3.set_border_width(10)
		courses= showBooks(dept,sem,"courses") #fetching course info and credits
		course_list_store = Gtk.ListStore(str, str, str, str, str , str)
		for course in courses:
			course_list_store.append(list(course))
		course_tree_view = Gtk.TreeView(course_list_store)

		for i, col_title in enumerate(["Course-Code", "Course Name", "L", "T", "P" , "C"]):
			renderer = Gtk.CellRendererText()

			column = Gtk.TreeViewColumn(col_title, renderer, text=i)
			column.set_sort_column_id(i)
			course_tree_view.append_column(column)

		self.page3.pack_start(course_tree_view, True, True, 0)
		self.notebook.append_page(self.page3, Gtk.Label('Course Information'))
		#adding the course page to notebook view

		self.page4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page4.set_border_width(10)
		grid = Gtk.Grid(column_homogeneous=True, column_spacing=10, row_spacing=10)

		self.scrolledwindow = Gtk.ScrolledWindow()
		self.scrolledwindow.set_policy(Gtk.PolicyType.NEVER,
									   Gtk.PolicyType.AUTOMATIC)

		self.liststore_files = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str, str)


		self.course_combo = Gtk.ComboBoxText()
		self.course_combo.set_entry_text_column(0)
		self.courseList = []
		self.activeFilename = ""
		self.activeRoll = ""
		for course in courses:
			self.courseList.append(str(course[0]))
		for course in self.courseList:
			self.course_combo.append_text(course)
		self.course_combo.connect('changed', self.on_course_combo_changed)

		self.course_combo.set_active(0)

		self.rating_combo = Gtk.ComboBoxText()
		self.rating_combo.set_entry_text_column(0)

		for i in range(1,6):
			self.rating_combo.append_text(str(i))
		self.rating_combo.connect('changed', self.on_rating_changed)

		self.rating_combo.set_active(4)	

		buttonbox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
		buttonbox.set_layout(Gtk.ButtonBoxStyle.EDGE)
		self.textBox = Gtk.Label("Rating For the File:")
		buttonbox.add(self.course_combo)
		buttonbox.add(self.textBox)
		buttonbox.add(self.rating_combo)

	
		self.button_rating = Gtk.Button("Submit Rating")
		self.button_rating.connect("clicked", self.on_rating_submit)
		buttonbox.add(self.button_rating)
	
		button_choose_file = Gtk.Button("Choose File")
		button_choose_file.connect("clicked", self.on_file_clicked)
		buttonbox.add(button_choose_file)

		button_upload = Gtk.Button("Upload")
		button_upload.connect("clicked", self.on_upload_clicked,roll)
		buttonbox.add(button_upload)

		button_download = Gtk.Button("Download")
		button_download.connect("clicked", self.on_download_clicked)
		buttonbox.add(button_download)

		self.updateFileList()
		grid.attach(self.scrolledwindow, 0, 0, 1, 1)
		grid.attach_next_to(buttonbox, self.scrolledwindow,
								 Gtk.PositionType.BOTTOM, 1, 1)

		self.page4.pack_start(grid, True, True, 0)
		self.notebook.append_page(self.page4, Gtk.Label('Notes'))


		#Book lending platform
		self.page5 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		self.page5.set_border_width(10)
		grid = Gtk.Grid(column_homogeneous=True, column_spacing=10, row_spacing=10)

		self.lendingwindow = Gtk.ScrolledWindow()
		self.lendingwindow.set_policy(Gtk.PolicyType.NEVER,
									   Gtk.PolicyType.AUTOMATIC)

		self.liststore_lend = Gtk.ListStore(str, str)

		self.books_combo = Gtk.ComboBoxText()
		self.books_combo.set_entry_text_column(0)
		
		self.books = courseBooks
		self.roll = roll
		self.activeLender = ""

		self.course_combo2 = Gtk.ComboBoxText()
		self.course_combo2.set_entry_text_column(0)
		for course in self.courseList:
			self.course_combo2.append_text(course)
		self.course_combo2.connect('changed', self.on_course_combo2_changed)

		self.course_combo2.set_active(0)
		for book in self.books:
			if book[1] == self.courseList[self.course_combo2.get_active()]:
				self.books_combo.append_text(book[2])
		self.books_combo.connect('changed', self.on_books_combo_changed)
		self.books_combo.set_active(0)
		lendButtonBox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
		lendButtonBox.set_layout(Gtk.ButtonBoxStyle.EDGE)

		lendButtonBox.add(self.course_combo2)
		lendButtonBox.add(self.books_combo)
	
		self.button_lend = Gtk.Button("Lend")
		self.button_lend.connect("clicked", self.on_lend_clicked)
		lendButtonBox.add(self.button_lend)

		self.contact_field = Gtk.Entry()
		lendButtonBox.add(self.contact_field)

		self.button_submit_lend = Gtk.Button("Submit")
		self.button_submit_lend.connect("clicked", self.on_submit_lend_clicked)
		lendButtonBox.add(self.button_submit_lend)

		self.button_delete = Gtk.Button("Delete")
		self.button_delete.connect("clicked", self.on_delete_clicked)
		lendButtonBox.add(self.button_delete)

		self.updateLendList()
		grid.attach(self.lendingwindow, 0, 0, 1, 1)
		grid.attach_next_to(lendButtonBox, self.lendingwindow,
								 Gtk.PositionType.BOTTOM, 1, 1)

		self.page5.pack_start(grid, True, True, 0)
		self.notebook.append_page(self.page5, Gtk.Label('Books Lend/Borrow'))

		Logout = Gtk.Button(label="Logout")
		Logout.connect("clicked", self.Logout) #button click event
		WindowBox.pack_start(Logout,True,True,0)

		self.add(WindowBox)

	# def on_treeview_click(self, treeview, path, view_column):
 #        model=treeview.get_model()
 #        action_id=model[path][0]
 #        url='....' # build your url
 #        webbrowser.open(url)
 	def on_rating_changed(self, widget):
 		pass	
 	def on_rating_submit(self,widget):
 		self.button_rating.hide()
 		# self.textBox.hide()
 		self.rating_combo.hide()
 		self.textBox.set_text("Thanks for your rating!")
 		pass

 	def hideLending(self):
 		try:
	 		self.button_lend.hide()
	 		self.contact_field.hide()
	 		self.button_submit_lend.hide()
	 	except:
	 		pass

 	def showLending(self):
 		try:
	 		self.button_lend.show()
	 		self.contact_field.hide()
	 		self.button_submit_lend.hide()
	 	except:
	 		pass

	def checkForDelete(self):
		try:
			if self.activeLender == self.roll:
				self.button_delete.show()
			else:
				self.button_delete.hide()
		except:
			pass

 	def on_submit_lend_clicked(self, widget):
 		lendBook(self.roll, self.contact_field.get_text(), self.courseList[self.course_combo2.get_active()], self.books_combo.get_active_text())
 		self.updateLendList()
 		self.hideLending()

 	def on_lend_clicked(self, widget):
 		self.button_lend.hide()
 		self.contact_field.show()
 		self.button_submit_lend.show()

 	def on_delete_clicked(self, widget):
 		deleteLender(self.roll, self.courseList[self.course_combo2.get_active()], self.books_combo.get_active_text())
 		self.updateLendList()

	def on_treeview_click(self, treeview,path,view_column):
		model=treeview.get_model()
		action_id=model[path][0]
		url="https://www.google.com"
		webbrowser.open(url)


 	def Logout(self,widget):
 		fi=open('.info.txt','w+')
 		fi.close()
 		Gtk.main_quit()
 	

	def on_course_combo_changed(self, combo):
		self.updateFileList()
		index = combo.get_active()
		combo.set_active(index)

	def on_course_combo2_changed(self, combo):
		self.updateLendList()
		self.books_combo.get_model().clear()
		for book in self.books:
			if book[1] == self.courseList[self.course_combo2.get_active()]:
				self.books_combo.append_text(book[2])
		self.books_combo.set_active(0)
		index = combo.get_active()
		combo.set_active(index)
		try:
			self.button_delete.hide()
		except:
			pass

	def on_books_combo_changed(self, combo):
		self.updateLendList()
		index = combo.get_active()
		combo.set_active(index)
		try:
			self.button_delete.hide()
		except:
			pass

	def getSelectedLenderDetails(self, tree_selection):
		(model, pathlist) = tree_selection.get_selected_rows()
		for path in pathlist:
			tree_iter = model.get_iter(path)
			self.activeLender = model.get_value(tree_iter,0)
		self.checkForDelete()

	def on_download_clicked(self,widget):
		dialog = Gtk.FileChooserDialog("Please choose a folder", self,
			Gtk.FileChooserAction.SELECT_FOLDER,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 "Select", Gtk.ResponseType.OK))
		dialog.set_default_size(800, 400)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			location = dialog.get_filename()
			activeCourse = self.courseList[self.course_combo.get_active()]
			downloadFile(self.activeFilename,location,activeCourse,self.activeRoll)
		dialog.destroy()
		self.button_rating.show()
		self.textBox.show()
		self.rating_combo.show()


	def on_upload_clicked(self, widget,roll):
		try:
			if self.fileToUpload != "":
				index = self.course_combo.get_active()
				course=self.courseList[index]
				uploadFile(self.fileToUpload, roll, course)
				self.updateFileList()
		except:
			pass

	def on_file_clicked(self, widget):
		dialog = Gtk.FileChooserDialog("Please choose a file", self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters(dialog)
		self.fileToUpload = ""
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.fileToUpload = dialog.get_filename()
		dialog.destroy()


	def add_filters(self, dialog):
		filter_text = Gtk.FileFilter()
		filter_text.set_name("Text files")
		filter_text.add_mime_type("text/plain")
		dialog.add_filter(filter_text)

		filter_py = Gtk.FileFilter()
		filter_py.set_name("Python files")
		filter_py.add_mime_type("text/x-python")
		dialog.add_filter(filter_py)

		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)


	def getSelectedFileDetails(self, tree_selection):
		(model, pathlist) = tree_selection.get_selected_rows()
		for path in pathlist:
			tree_iter = model.get_iter(path)
			self.activeFilename = model.get_value(tree_iter,1)
			self.activeRoll = model.get_value(tree_iter,2)


	def updateFileList(self):
		pics_list,pics_name,uploader_list,upload_time = listUploads(self.courseList[self.course_combo.get_active()])
		self.liststore_files.clear()
		for name, pic, uploader, time in zip(pics_name, pics_list, uploader_list, upload_time):
			pxbf = GdkPixbuf.Pixbuf.new_from_file_at_scale(pic, 50, 50, True)
			self.liststore_files.append([pxbf, name, uploader, time])

		self.treeview = Gtk.TreeView(model=self.liststore_files)
		self.treeview.set_hexpand(True)
		self.treeview.set_vexpand(True)
		# creamos las columnas del TreeView
		renderer_pixbuf = Gtk.CellRendererPixbuf()
		column_pixbuf = Gtk.TreeViewColumn('Preview', renderer_pixbuf, pixbuf=0)
		column_pixbuf.set_alignment(0.5)
		self.treeview.append_column(column_pixbuf)

		renderer_text = Gtk.CellRendererText(weight=600)
		renderer_text.set_fixed_size(200, -1)
		renderer_text.set_alignment(0.5,0.5)

		column_text = Gtk.TreeViewColumn('Filename', renderer_text, text=1)
		column_text.set_sort_column_id(1)
		column_text.set_alignment(0.5)
		self.treeview.append_column(column_text)

		renderer_text = Gtk.CellRendererText(weight=600)
		renderer_text.set_fixed_size(200, -1)
		renderer_text.set_alignment(0.5,0.5)

		column_text = Gtk.TreeViewColumn('Uploaded By', renderer_text, text=2)
		# column_text.set_sort_column_id(1)
		column_text.set_alignment(0.5)
		self.treeview.append_column(column_text)

		renderer_text = Gtk.CellRendererText()
		renderer_text.set_fixed_size(200, -1)
		renderer_text.set_alignment(0.5,0.5)

		column_text = Gtk.TreeViewColumn('Upload time', renderer_text, text=3)
		column_text.set_sort_column_id(3)
		column_text.set_alignment(0.5)
		self.treeview.append_column(column_text)      

		tree_selection = self.treeview.get_selection()

		tree_selection.connect("changed", self.getSelectedFileDetails)

		self.scrolledwindow.add_with_viewport(self.treeview)  


	def updateLendList(self):
		rolls, contacts = listLenders(self.courseList[self.course_combo2.get_active()], self.books_combo.get_active_text())
		self.liststore_lend.clear()
		for roll,contact in zip(rolls,contacts):
			self.liststore_lend.append([roll, contact])
		
		if self.roll in rolls or self.books_combo.get_active_text() is None:
			self.hideLending()
		else:
			self.showLending()
		
		treeview = Gtk.TreeView(model=self.liststore_lend)
		treeview.set_hexpand(True)
		treeview.set_vexpand(True)

		renderer_text = Gtk.CellRendererText(weight=600)
		renderer_text.set_fixed_size(200, -1)
		renderer_text.set_alignment(0.5,0.5)

		column_text = Gtk.TreeViewColumn('Roll number', renderer_text, text=0)
		column_text.set_sort_column_id(1)
		column_text.set_alignment(0.5)
		treeview.append_column(column_text)

		renderer_text = Gtk.CellRendererText(weight=600)
		renderer_text.set_fixed_size(200, -1)
		renderer_text.set_alignment(0.5,0.5)

		column_text = Gtk.TreeViewColumn('Contact no.', renderer_text, text=1)
		column_text.set_alignment(0.5)
		treeview.append_column(column_text)

		tree_selection = treeview.get_selection()
		tree_selection.connect("changed", self.getSelectedLenderDetails)

		self.lendingwindow.add_with_viewport(treeview)


class MainBox(Gtk.Window):

	def __init__(self):
		
		Gtk.Window.__init__(self, title="SemBegins!") #main window
		# self.set_default_size(200, 100) #setting default size
		self.set_border_width(10)	
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
		label = Gtk.Label("Enter Your Roll Number:")
		vbox.pack_start(label, True, True, 0)
		
		self.entry = Gtk.Entry() #entry box
		self.entry.set_max_length(9) 
		self.entry.set_text("140101063") #default text value
		vbox.pack_start(self.entry, True, True, 0)
		fi.write(self.entry.get_text())

		button = Gtk.Button(label="Submit")
		button.connect("clicked", self.buttonClicked) #button click event
		vbox.pack_start(button, True, True, 0)
		self.add(vbox)
		

		

	def buttonClicked(self, widget):
		self.roll=self.entry.get_text()
		self.sem=semFinder(self.roll)
		self.dept=depFinder(self.roll)
		displayResult(self.dept, self.sem, self.roll)


fi=open(".info.txt",'r+')
line=fi.readline()

if line == '':
	win = MainBox() #calling the mainbox
	win.connect("delete-event", Gtk.main_quit) #adding the quit event listener
	win.show_all()
	Gtk.main()
else:
	displayResult(depFinder(line),semFinder(line),line)

fi.close();