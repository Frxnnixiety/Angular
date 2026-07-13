import { Component, signal, inject, OnInit} from '@angular/core';
import { RouterOutlet } from '@angular/router';

// Importamos el servicio y la interfaz estructurada hace un momento
import { Api, Products} from './services/api';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html', // Vinculado a tu archivo HTML
  styleUrl: './app.css'
})
export class App implements OnInit {
  
  // Este método se ejecuta automáticamente cuando se genera la vista en el navegador
  ngOnInit(): void {
    this.getProducts();
  }

  protected readonly title = signal('eshop');
  
  // Inyección del servicio de datos en el componente
  private readonly apiService = inject(Api);  
  
  // Se crea una señal (signal) para detectar de forma reactiva los cambios del arreglo
  productList = signal<Products[]>([]);

  /**
   * Método para obtener los productos en formato JSON
   */
  getProducts() {
    this.apiService.getProducts().subscribe({
      next: (data) => {
        this.productList.set(data); // Actualizamos el estado de la señal con los datos recibidos
        console.log(data);
      },
      error: (err) => console.error('Error en GET:', err)
    });
  }

  /**
   * Método para eliminar un producto seleccionando su ID
   */
  deleteProduct(id: number) {
    this.apiService.deleteProduct(id).subscribe({
      next: (data) => {
        this.getProducts(); // Refrescamos la lista actual instalada
      },
      error: (err) => console.error('Error en DELETE:', err)
    });
  }
}