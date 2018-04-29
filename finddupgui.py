import os
import os.path
import threading
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk

import finddup

class FindDupGUI(tkinter.ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.nombre = 'FindDupGUI'

        self.configurar_master()
        self.pack(expand=tkinter.YES, fill=tkinter.BOTH)
        self.crear_widgets()

    def configurar_master(self):
        self.master.title(self.nombre)
        self.master['padx'] = 10
        self.master['pady'] = 10
        self.master.geometry('750x500')

    def crear_widgets(self):
        self.padding = {'padx': 5, 'pady': 5}

        a = tkinter.ttk.Frame(self)
        a.pack(fill=tkinter.X)

        tkinter.ttk.Label(a, text='Ubicación:').pack(**self.padding, side=tkinter.LEFT)

        self.ubicacion = tkinter.StringVar()
        tkinter.ttk.Entry(a, textvariable=self.ubicacion).pack(**self.padding, side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.X)

        tkinter.ttk.Button(a, text='...', command=self.seleccionar_carpeta).pack(**self.padding, side=tkinter.LEFT)

        self.buscar_boton = tkinter.ttk.Button(a, text='Buscar', command=self.buscar)
        self.buscar_boton.pack(**self.padding)

        b = tkinter.ttk.Frame(self)
        b.pack(fill=tkinter.X)

        self.seleccionar_duplicados = tkinter.ttk.Button(b, text='Seleccionar duplicados', command=self.seleccionar_duplicados)
        self.seleccionar_duplicados.pack(**self.padding, side=tkinter.LEFT)

        self.no_seleccionar = tkinter.ttk.Button(b, text='No seleccionar ninguno', command=self.no_seleccionar)
        self.no_seleccionar.pack(**self.padding, side=tkinter.LEFT)

        self.eliminar = tkinter.ttk.Button(b, text='Eliminar...', command=self.eliminar)
        self.eliminar.pack(**self.padding, side=tkinter.LEFT)

        self.listado = tkinter.ttk.Treeview(self, columns=('Ubicación'), height=5)
        self.listado.heading('#0', text='Hash MD5')
        self.listado.heading('Ubicación', text='Ubicación')
        self.listado.column('#0', width=250, stretch=tkinter.NO)
        self.listado.pack(**self.padding, expand=tkinter.YES, fill=tkinter.BOTH)

        self.estado = tkinter.StringVar()
        self.estado.set('Listo.')
        tkinter.ttk.Label(self, textvariable=self.estado).pack(**self.padding, fill=tkinter.X)

    def seleccionar_carpeta(self):
        ubicacion = tkinter.filedialog.askdirectory()
        if ubicacion:
            self.ubicacion.set(ubicacion)

    def borrar_listado(self):
        self.listado.delete(*self.listado.get_children())

    def borrar_unicos(self):
        for item in self.listado.get_children():
            if len(self.listado.get_children(item)) == 1:
                self.listado.delete(item)

    def buscar(self):
        if not os.path.isdir(self.ubicacion.get()):
            tkinter.messagebox.showerror(self.nombre, 'La ubicación especificada no existe.')
            return

        self.borrar_listado()

        self.buscar_boton['state'] = tkinter.DISABLED
        self.estado.set('Procesando...')

        self.busqueda = threading.Thread(target=self.buscar_thread)
        self.busqueda.start()

        self.after(500, self.esperar)

    def buscar_thread(self):
        for hash, ocurrencias in finddup.get_duplicate_files(str(self.ubicacion.get())):
            item = self.listado.insert('', tkinter.END, text=hash, open=tkinter.YES)

            for ocurrencia in ocurrencias:
                self.listado.insert(item, tkinter.END, values=(ocurrencia,))

    def esperar(self):
        if self.busqueda.is_alive():
            self.after(500, self.esperar)
        else:
            self.buscar_boton['state'] = tkinter.NORMAL
            self.estado.set('Listo.')

            if len(self.listado.get_children()) == 0:
                tkinter.messagebox.showinfo(self.nombre, 'No se encontraron archivos duplicados.')

    def seleccionar_duplicados(self):
        for item in self.listado.get_children():
            for item in self.listado.get_children(item)[1:]:
                self.listado.selection_add(item)

    def no_seleccionar(self):
        self.listado.selection_set()

    def eliminar(self):
        # blocking?
        eliminar_archivos = tkinter.messagebox.askyesno(self.nombre, '¿Eliminar archivos seleccionados?')

        if eliminar_archivos:
            n = 0
            for item in self.listado.selection():
                archivo = self.listado.item(item)['values'][0]

                try:
                    os.remove(archivo)
                except PermissionError:
                    print('PermissionError', archivo) ###debug
                else:
                    self.listado.delete(item)
                    n += 1

            self.borrar_unicos()

            if n == 1:
                mensaje = 'Se eliminó un archivo.'
            else:
                mensaje = f'Se eliminaron {n} archivos.'
            tkinter.messagebox.showinfo(self.nombre, mensaje)


if __name__ == '__main__':
    root = tkinter.Tk()
    FindDupGUI(root)
    root.mainloop()
